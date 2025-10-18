import numpy as np

from env import UAVCombatEnv
import time
import os
import json
import datetime
from openai import OpenAI


class UAVCombatAI:
    def __init__(self, config_file='../api.json', use_model="gpt-4o-mini"):
        """初始化AI空战决策系统"""
        # 加载配置

        with open(config_file) as f:
            config = json.load(f)
            os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
            os.environ["OPENAI_BASE_URL"] = config["OPENAI_BASE_URL"]

        self.use_model = use_model
        self.client = OpenAI()
        self.first_detection_done = False
        # 初始化空战环境
        self.env = UAVCombatEnv()

        # 历史信息存储
        self.state_history = []  # 存储历史状态
        self.action_history = []  # 存储历史动作
        self.reward_history = []  # 存储历史奖励

        # 决策记录存储
        self.decision_log = []  # 存储详细决策过程
        self.combat_sessions = []  # 存储每局对战信息
        self.action_lock = [False, False]  # [飞机0锁定, 飞机1锁定]
        self.last_action = [0, 0]  # 记录上次动作

        # 状态字段映射
        self.state_fields = [
            "longitude",  # 1 - 经度
            "latitude",  # 2 - 纬度
            "altitude",  # 3 - 高度
            "roll",  # 4 - 翻滚角
            "pitch",  # 5 - 俯仰角
            "yaw",  # 6 - 航向角
            "V",  # 7 - 速度
            "capture",  # 8 - 是否捕获到目标
            "captureTime",  # 9 - 捕获时间
            "targetDir",  # 10 - 与敌方的角度
            "targetDis",  # 11 - 与敌方的距离
        ]

    def parse_state_info(self, state_data):
        """
        解析状态信息为可读格式
        state_data: np.array 或 list，长度应 >= len(self.state_fields)
        返回: dict，字段名 -> 值
        """
        parsed_info = {}

        for i, field_name in enumerate(self.state_fields):
            if i < len(state_data):
                parsed_info[field_name] = float(state_data[i])

        # 处理航向角，如果 yaw 是弧度则转换为度
        if 'yaw' in parsed_info:
            import math
            yaw_value = parsed_info['yaw']
            # 假设 yaw 已经是角度，如果是弧度，则用 math.degrees()
            parsed_info['yaw_angle_degrees'] = yaw_value

        return parsed_info

    def create_situation_prompt_two_agents(self, state_agent0, state_agent1, recent_history=4):
        """
        为两架友机构造态势提示（集中式，一次决策两机）
        state_agent*: 11维归一化状态，与 UAVCombatEnv.get_normalized_state 输出一致
        """
        def denorm(s):
            low = np.array([-180, -90, 0.0, -90.0, -90.0, 0, 0.0, 0, 0.0, 0.0, 0.0], dtype=np.float32)
            high = np.array([180, 90, 8000.0, 90.0, 90.0, 360, 500.0, 1, 1000.0, 360.0, 100000.0], dtype=np.float32)
            return low + s * (high - low)

        s0 = denorm(np.array(state_agent0))
        s1 = denorm(np.array(state_agent1))

        prompt = f"""
    你是无人机编队的战术决策AI，控制两架己方无人机（编号0与1）。
    当前任务：在战区内协同接力搜索与监视敌方目标，当发现敌方时由一架下扎或攻击，另一架保持扫描或支援。目标是持续探测、确保目标不丢失，并在时机合适时发动攻击。
    
    坐标系：北东地系（正北为0°）。
    
    --- 飞机0（ID 0）状态 ---
    经度: {s0[0]:.6f}°，纬度: {s0[1]:.6f}°，高度: {s0[2]:.1f}m
    姿态: roll={s0[3]:.1f}°，pitch={s0[4]:.1f}°，yaw={s0[5]:.1f}°
    速度: {s0[6]:.1f}m/s
    捕获状态: {"✅ 已捕获" if s0[7]>0.5 else "❌ 未捕获"}
    捕获持续时间: {s0[8]:.1f}s
    目标方位: {s0[9]:.1f}°，目标距离: {s0[10]:.1f}m
    
    --- 飞机1（ID 1）状态 ---
    经度: {s1[0]:.6f}°，纬度: {s1[1]:.6f}°，高度: {s1[2]:.1f}m
    姿态: roll={s1[3]:.1f}°，pitch={s1[4]:.1f}°，yaw={s1[5]:.1f}°
    速度: {s1[6]:.1f}m/s
    捕获状态: {"✅ 已捕获" if s1[7]>0.5 else "❌ 未捕获"}
    捕获持续时间: {s1[8]:.1f}s
    目标方位: {s1[9]:.1f}°，目标距离: {s1[10]:.1f}m
    
    ⚙️ 宏动作编号（底层逻辑已封装）：
    0. Search — 搜索或巡航模式（默认巡逻/未发现目标时）
    1. Keep   — 保持上次动作
    2. GoStright — 保持当前航向直行
    3. TurnLeft — 左转机动
    4. TurnRight — 右转机动
    5. approch — 靠近目标（⚠️ 仅当“已捕获目标”时有效）
    6. attack — 下扎攻击（⚠️ 仅当“已捕获目标”时有效）
    
    🎯 决策要点：
    1. 若任一架捕获目标（capture=True），优先分工：一架保持接力监视，另一架选择靠近/攻击。
    2. 若捕获到目标需要尽快下扎攻击。
    3. 若目标距离近、角度有利且捕获持续时间较长，可允许一架发起 attack。
    4. 若两架同时捕获同一目标，应避免重复攻击，一机进攻，一机支援或绕行。
    5. 若捕获状态为 False，则 approch 或 attack 动作无效，请避免使用。
    6. 下扎攻击的时候，尽量不要再产生其他动作而是输出action=1,保持就行。
    7. 宏动作5和6只有在捕获到敌方的时候才有效，否则无效。
    请基于上述态势，输出两架飞机的宏动作编号与简要理由。
    
    输出格式（必须严格遵守）：
    Plane0: [数字 1-6]
    Plane1: [数字 1-6]
    简短理由: [一句话说明主要决策依据]
    
    示例：
    Plane0: 6
    Plane1: 1
    简短理由: 飞机0已捕获且距离近，执行攻击；飞机1保持搜索接力目标。
    """

        # 添加历史（可选）
        if hasattr(self, "action_history") and len(self.action_history) > 0:
            prompt += "\n近期行动历史（最近{}步）：\n".format(min(recent_history, len(self.action_history)))
            start = max(0, len(self.action_history) - recent_history)
            for i in range(start, len(self.action_history)):
                a = self.action_history[i]
                prompt += f"- Step {i+1}: {a}\n"

        return prompt

    def get_action_name(self, action):
        """获取动作名称"""
        action_names = {
            0: "初始搜索模式",
            1: "保持上次",
            2: "直线行驶",
            3: "左转机动",
            4: "右转机动",
            5: "靠近目标",
            6: "下扎攻击",
        }
        return action_names.get(action, f"未知动作({action})")

    def make_decision_two_agents(self, current_state, episode_num, step_num):
        """
        使用大模型做出两架飞机集中式决策（带首次搜索限制 + 下扎锁定）
        """
        try:
            # 提取捕获状态
            s0_capture = current_state[7] > 0.5
            s1_capture = current_state[18] > 0.5

            # 初始化动作锁（首次运行时）
            if not hasattr(self, "action_lock"):
                self.action_lock = [False, False]  # [飞机0锁定, 飞机1锁定]
                self.last_action = [0, 0]  # 记录上次动作

            # -------------------------------
            # 1️⃣ 首次发现前：任意一架捕获敌方就启用AI决策
            # -------------------------------
            if not self.first_detection_done:
                if s0_capture or s1_capture:
                    self.first_detection_done = True
                    print("\n⚠️ 首次发现敌方目标，启用AI战术决策。")
                else:
                    actions = [1, 1]  # 初始搜索模式
                    print(f"\nAI战术分析（两机）：首次发现敌方前，保持初始搜索动作 [1,1]")
                    decision_record = {
                        'episode': episode_num,
                        'step': step_num,
                        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'state': current_state.copy(),
                        'ai_analysis': "首次发现敌方前默认搜索动作",
                        'chosen_action': actions
                    }
                    self.decision_log.append(decision_record)
                    return actions

            # -------------------------------
            # 2️⃣ 若两机均被锁定，则无需LLM推理
            # -------------------------------
            if all(self.action_lock):
                actions = [1, 1]
                ai_response = "两机均处于下扎阶段，保持动作1。"
                print(f"\nAI战术分析（两机）：{ai_response}")
                decision_record = {
                    'episode': episode_num,
                    'step': step_num,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'state': current_state.copy(),
                    'ai_analysis': ai_response,
                    'chosen_action': actions
                }
                self.decision_log.append(decision_record)
                return actions

            # -------------------------------
            # 3️⃣ LLM 决策（仅对未锁定飞机）
            # -------------------------------
            state0 = current_state[:11]
            state1 = current_state[11:]
            situation_prompt = self.create_situation_prompt_two_agents(state0, state1)

            response = self.client.chat.completions.create(
                model=self.use_model,
                messages=[
                    {"role": "system",
                     "content": "你是一名经验丰富的无人机空战飞行员AI，具备专业战术决策能力。为两架飞机输出1-6动作编号。"},
                    {"role": "user", "content": situation_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            ai_response = response.choices[0].message.content
            print(f"\nAI战术分析（两机）：\n{ai_response}")

            import re
            actions_found = re.findall(r'\b([0-6])\b', ai_response)
            if len(actions_found) >= 2:
                actions_llm = [int(actions_found[0]), int(actions_found[1])]
            else:
                print("解析AI动作失败，使用默认动作 [1,1]")
                actions_llm = [1, 1]

            # -------------------------------
            # 4️⃣ 合并锁定逻辑：锁定飞机动作固定为1，未锁定使用LLM输出
            # -------------------------------
            actions = [0, 0]
            for i in range(2):
                if self.action_lock[i]:
                    # 锁定飞机：动作固定为1
                    actions[i] = 1
                else:
                    # 未锁定飞机：使用LLM动作
                    actions[i] = actions_llm[i]
                    if actions[i] == 6:
                        # 新进入下扎 -> 上锁，并动作固定为1
                        self.action_lock[i] = True
                        actions[i] = 1
                        print(f"🚀 飞机{i}进入下扎攻击状态，动作锁定，后续保持动作1。")
                    else:
                        # 普通动作更新上次动作
                        self.last_action[i] = actions[i]

            # -------------------------------
            # 5️⃣ 自动解除锁（例如捕获丢失或高度恢复）
            # -------------------------------
            for i in range(2):
                alt = current_state[2] if i == 0 else current_state[13]
                capture = current_state[7] if i == 0 else current_state[18]
                if self.action_lock[i] and (alt > 3000 or capture < 0.5):
                    self.action_lock[i] = False
                    print(f"🟢 飞机{i}解除下扎锁定（高度或捕获状态恢复）。")

            # -------------------------------
            # 6️⃣ 记录日志
            # -------------------------------
            decision_record = {
                'episode': episode_num,
                'step': step_num,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'state': current_state.copy(),
                'ai_analysis': ai_response,
                'chosen_action': actions.copy(),
                'locked_state': self.action_lock.copy()
            }
            self.decision_log.append(decision_record)

            return actions

        except Exception as e:
            print(f"AI决策出错: {e}, 使用默认动作 [1,1]")
            actions = [1, 1]
            decision_record = {
                'episode': episode_num,
                'step': step_num,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'state': current_state.copy(),
                'ai_analysis': f"决策出错: {e}",
                'chosen_action': actions,
                'error': str(e)
            }
            self.decision_log.append(decision_record)
            return actions

    def run_combat_simulation_two_agents(self, epochs=3, max_steps=1000):
        """
        运行空战仿真 - 两架飞机集中式决策
        """
        print("=" * 80)
        print("AI空战决策系统启动（两机集中式）")
        print("=" * 80)

        def denorm_state(s):
            low = np.array([-180, -90, 0.0, -90.0, -90.0, 0, 0.0, 0, 0.0, 0.0, 0.0], dtype=np.float32)
            high = np.array([180, 90, 8000.0, 90.0, 90.0, 360, 500.0, 1, 1000.0, 360.0, 100000.0], dtype=np.float32)
            return low + s * (high - low)

        for epoch in range(epochs):
            print(f"\n第 {epoch + 1} 局对战开始...")
            obs, info = self.env.reset()
            ep_reward = 0.0
            step_count = 0
            done = False

            episode_states = []
            episode_actions = []
            episode_rewards = []

            while not done and step_count < max_steps:
                step_count += 1

                s0 = denorm_state(obs[:11])
                s1 = denorm_state(obs[11:])
                print(f"飞机0: 高度={s0[2]:.1f}m, 捕获={s0[7] > 0.5}, 目标距离={s0[10]:.1f}m")
                print(f"飞机1: 高度={s1[2]:.1f}m, 捕获={s1[7] > 0.5}, 目标距离={s1[10]:.1f}m")

                # 集中式LLM决策
                actions = self.make_decision_two_agents(obs, epoch + 1, step_count)
                print(f"AI决策: 飞机0 -> {actions[0]}, 飞机1 -> {actions[1]}")

                # 执行动作
                obs, reward, terminated, truncated, info = self.env.step(actions)
                ep_reward += float(reward) if reward is not None else 0.0

                # 记录历史
                episode_states.append(obs.copy())
                episode_actions.append(actions)
                episode_rewards.append(float(reward) if reward is not None else 0.0)

                # 更新决策日志 reward
                self.decision_log[-1]['reward'] = float(reward) if reward is not None else 0.0

                self.env.render()

                if reward != 0:
                    print(f"本步奖励: {reward:.2f}")

                if terminated or truncated:
                    done = True
                    print(f"\n对战结束! 最终奖励: {ep_reward:.2f}")

                # 保存全局历史
            self.state_history.extend(episode_states[-50:])
            self.action_history.extend(episode_actions[-10:])
            self.reward_history.extend(episode_rewards[-10:])
            max_history = 100
            if len(self.state_history) > max_history:
                self.state_history = self.state_history[-max_history:]
                self.action_history = self.action_history[-max_history:]
                self.reward_history = self.reward_history[-max_history:]

            # 本局动作统计
            from collections import Counter
            actions0 = [a[0] for a in episode_actions]
            actions1 = [a[1] for a in episode_actions]
            action_counts0 = dict(Counter(actions0))
            action_counts1 = dict(Counter(actions1))
            avg_reward = sum(episode_rewards) / len(episode_rewards) if episode_rewards else 0.0

            print(f"\n第 {epoch + 1} 局总奖励: {ep_reward:.1f}, 平均步奖励: {avg_reward:.3f}")
            print("动作使用统计 (飞机0, 飞机1):", action_counts0, action_counts1)

            # 保存回合信息
            session_info = {
                'episode': epoch + 1,
                'total_reward': ep_reward,
                'avg_reward': avg_reward,
                'total_steps': step_count,
                'actions_used': episode_actions.copy(),
                'rewards': episode_rewards.copy(),
                'action_counts0': action_counts0,
                'action_counts1': action_counts1,
                'start_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.combat_sessions.append(session_info)

        print("\n" + "="*80)
        print("所有对战完成!")
        if self.reward_history:
            total_avg_reward = sum(self.reward_history)/len(self.reward_history)
            print(f"总体平均奖励: {total_avg_reward:.3f}")

        # 生成决策报告
        self.generate_decision_report()

    def generate_decision_report(self):
        """生成两机决策历史完整markdown报告"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uav_combat_decisions_two_agents_{timestamp}.md"

        def denorm_state(s):
            low = np.array([-180, -90, 0.0, -90.0, -90.0, 0, 0.0, 0, 0.0, 0.0, 0.0], dtype=np.float32)
            high = np.array([180, 90, 8000.0, 90.0, 90.0, 360, 500.0, 1, 1000.0, 360.0, 100000.0], dtype=np.float32)
            return low + s * (high - low)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# UAV空战AI两机决策历史报告\n\n")
            f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"使用模型: {self.use_model}\n")
            f.write(f"总对战局数: {len(self.combat_sessions)}\n")
            f.write(f"总决策步数: {len(self.decision_log)}\n\n")

            f.write("## 对战概览\n\n")
            f.write("| 局数 | 总奖励 | 步数 | 平均奖励 | 主要动作(飞机0/飞机1) |\n")
            f.write("|------|--------|------|----------|----------------|\n")
            for session in self.combat_sessions:
                main_action0 = max(session['action_counts0'], key=session['action_counts0'].get)
                main_action1 = max(session['action_counts1'], key=session['action_counts1'].get)
                main_action_name = f"{self.get_action_name(main_action0)}/{self.get_action_name(main_action1)}"
                f.write(f"| {session['episode']} | {session['total_reward']:.1f} | "
                        f"{session['total_steps']} | {session['avg_reward']:.3f} | {main_action_name} |\n")

            f.write("\n## 详细决策记录\n\n")
            current_episode = 0
            for i, decision in enumerate(self.decision_log):
                if decision['episode'] != current_episode:
                    current_episode = decision['episode']
                    f.write(f"\n### 第{current_episode}局对战\n\n")

                f.write(f"#### 步骤 {decision['step']} - {decision['timestamp']}\n\n")

                state_vec = decision['state']
                state0 = denorm_state(state_vec[:11])
                state1 = denorm_state(state_vec[11:])

                f.write("**飞机0状态:**\n")
                for idx, val in enumerate(state0):
                    f.write(f"- 索引{idx}: {val:.3f}\n")
                f.write("\n**飞机1状态:**\n")
                for idx, val in enumerate(state1):
                    f.write(f"- 索引{idx}: {val:.3f}\n")

                f.write("\n**AI战术分析:**\n```\n")
                f.write(decision['ai_analysis'])
                f.write("\n```\n")

                f.write("\n**决策结果:**\n")
                chosen_action = decision['chosen_action']
                f.write(f"- 飞机0行动: {chosen_action[0]} - {self.get_action_name(chosen_action[0])}\n")
                f.write(f"- 飞机1行动: {chosen_action[1]} - {self.get_action_name(chosen_action[1])}\n")
                if 'reward' in decision:
                    f.write(f"- 获得奖励: {decision['reward']:.3f}\n")
                if 'error' in decision:
                    f.write(f"- ⚠️ 错误: {decision['error']}\n")
                f.write("\n---\n")

        print(f"\n决策历史报告已保存到: {filename}")
        return filename


if __name__ == "__main__":
    try:
        # 初始化 AI 空战系统
        combat_ai = UAVCombatAI(
            config_file="../api.json",
            use_model='Qwen/Qwen3-30B-A3B-Instruct-2507'
            # use_model='Qwen/Qwen3-Next-80B-A3B-Instruct'  # 确保和你 JSON 配置、ModelScope 服务一致
        )

        # 运行两机集中式仿真
        combat_ai.run_combat_simulation_two_agents(epochs=1, max_steps=500)

    except KeyboardInterrupt:
        print("\n用户中断程序")

    except Exception as e:
        print(f"程序出错: {e}")

    finally:
        print("程序结束")
