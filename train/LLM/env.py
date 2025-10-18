import os
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from environment import AirCombat_demo as env
from stable_baselines3.common.env_checker import check_env

class UAVCombatEnv(gym.Env):
    """Custom Environment for UAV Combat - Two Agents"""

    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(UAVCombatEnv, self).__init__()

        self.state_dimension = 11
        self.current_step = 0
        self.env = env

        # ----------------- Observation Space -----------------
        low_array = np.array([
            -180, -90, 0.0, -90.0, -90.0, 0, 0.0,
            0, 0.0, 0.0, 0.0
        ], dtype=np.float32)

        high_array = np.array([
            180, 90, 8000.0, 90.0, 90.0, 360, 500.0,
            1, 1000.0, 360.0, 100000.0
        ], dtype=np.float32)

        self.low_array = low_array
        self.high_array = high_array

        # 每架飞机的状态
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(self.state_dimension*2,),  # 两架飞机状态拼接
            dtype=np.float32
        )

        # ----------------- Action Space -----------------
        self.action_space = spaces.MultiDiscrete([6, 6])  # 两架飞机动作

        self.episode = 0

    # ---------------------------------------------------------
    def reset(self, seed=None):
        super().reset(seed=seed)
        os.system("taskkill /IM simulation_603.exe /F")

        self.current_step = 0
        self.env.EnvInit(self.episode, [0, 0])
        self.env.UpdateState()

        # 返回两架飞机状态
        obs0 = self.get_normalized_state(agent_id=0)
        obs1 = self.get_normalized_state(agent_id=1)

        return np.concatenate([obs0, obs1], axis=0), {}

    # ---------------------------------------------------------
    def step(self, actions):
        """
        actions: list[int] 或 np.array, 长度2，对应两架飞机
        返回: 拼接后的两架飞机状态, reward, terminated, truncated, info
        """
        # 确保传给 C++ 的是 list[int]
        if isinstance(actions, np.ndarray):
            actions = actions.astype(int).tolist()
        elif isinstance(actions, (list, tuple)):
            actions = [int(a) for a in actions]
        else:
            raise TypeError(f"Unsupported action type: {type(actions)}")
        flag = True
        # 每步重复执行底层动作10次
        for _ in range(100):
            self.env.EnvStep_PathTomonitor(actions, flag)
            flag = False

        self.env.UpdateState()
        self.current_step += 1

        obs0 = self.get_normalized_state(agent_id=0)
        obs1 = self.get_normalized_state(agent_id=1)
        new_state = np.concatenate([obs0, obs1], axis=0)

        # 奖励函数（测试阶段设为 0）
        reward = 0.0

        terminated = False  # 任务自然结束条件
        truncated = self.current_step >= 1000  # 最大步数

        info = {}

        return new_state, reward, terminated, truncated, info

    # ---------------------------------------------------------
    def get_normalized_state(self, agent_id=0):
        """
        获取单架飞机状态并标准化到 [0,1]
        """
        states = self.env.States()  # list[PlaneState_S, PlaneState_S]
        s = states[agent_id]

        raw_vec = np.array([
            s.longitude,
            s.latitude,
            s.altitude,
            s.roll,
            s.pitch,
            s.yaw,
            s.V,
            s.capture,
            s.captureTime,
            s.targetDir,
            s.targetDis
        ], dtype=np.float32)

        normalized_vec = (raw_vec - self.low_array) / (self.high_array - self.low_array)
        normalized_vec = np.clip(normalized_vec, 0.0, 1.0)

        return normalized_vec.astype(np.float32)

    # ---------------------------------------------------------
    def render(self):
        pass

    def close(self):
        pass

# ---------------------------------------------------------
if __name__ == '__main__':
    env = UAVCombatEnv()
    check_env(env, warn=True)

    print("✅ 环境检查通过")

    obs, info = env.reset()
    print("初始状态：", obs.shape)  # 22维

    for i in range(5):
        # 随机动作
        action = env.action_space.sample()  # [动作0, 动作1]
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {i+1}: action={action}, obs.shape={obs.shape}")
