from environment import AirCombat_demo as env

env.EnvInit(1, [0,0])

Plane_0 = env.Planes()[0]
Plane_1 = env.Planes()[1]
State_0 = env.States()[0]

action_0 = 1
action_1 = 1
while True:
    env.EnvStep_PathTomonitor([action_0, action_1], True)
    # env.EnvStep_YingFei([[0.6, 0.000, 0], [0.6, 6000, 90]], True)
    env.UpdateState()
    if State_0.capture:
        action_0=5
    if env.TargetDone():
        break
