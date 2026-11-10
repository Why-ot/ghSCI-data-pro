import time, json
from piper_sdk import C_PiperInterface_V2
YST = {"can0":[103.04,83.53,-78.85,70.48,4.79,13.96],
       "can1":[-5.95,116.05,-91.34,-58.75,27.12,34.98]}
res={}
for ch in ("can0","can1"):
    p = C_PiperInterface_V2(ch); p.ConnectPort(); time.sleep(0.7)
    js = p.GetArmJointMsgs().joint_state
    deg=[round(x/1000.0,2) for x in (js.joint_1,js.joint_2,js.joint_3,js.joint_4,js.joint_5,js.joint_6)]
    d=[round(deg[i]-YST[ch][i],2) for i in range(6)]
    res[ch]={"deg":deg,"delta":d}
    print(ch,"now:",deg,"| vs 11-06:",d)
json.dump(res,open("/home/yuanyou/R3A_CAPTURE/pose_20261109.json","w"),indent=2)
print("saved")