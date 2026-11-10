#!/usr/bin/env python3
"""坐标系映射诊断 — 逐项测试 VR 手柄与机械臂末端运动对应关系"""
import rospy
import numpy as np
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
from tf.transformations import euler_from_quaternion
import threading
import json
from datetime import datetime

class CoordDiagnostic:
    def __init__(self, side):
        self.side = side
        self.lock = threading.Lock()
        self.vr_pose = None
        self.vr_base = None
        self.vr_calibrated = False
        self.joint_pos = None

        topic = '/right_handle_pose' if side == 'right' else '/left_handle_pose'
        rospy.Subscriber(topic, PoseStamped, self._vr_cb, queue_size=1)
        rospy.Subscriber('/puppet/joint_' + side, JointState, self._joint_cb, queue_size=1)

    def _vr_cb(self, msg):
        with self.lock:
            pos = msg.pose.position
            quat = msg.pose.orientation
            rpy = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])
            self.vr_pose = [pos.x, pos.y, pos.z, rpy[0], rpy[1], rpy[2]]

    def _joint_cb(self, msg):
        with self.lock:
            if len(msg.position) >= 6:
                self.joint_pos = list(msg.position[:6])

    def calibrate(self):
        with self.lock:
            if self.vr_pose is not None:
                self.vr_base = list(self.vr_pose)
                self.vr_calibrated = True
                return True
        return False

    def get_delta(self):
        with self.lock:
            if not self.vr_calibrated or self.vr_pose is None or self.vr_base is None:
                return None
            return [self.vr_pose[i] - self.vr_base[i] for i in range(6)]

    def get_joints(self):
        with self.lock:
            return list(self.joint_pos) if self.joint_pos else None

def fmt_delta(d):
    return "pos=[%+7.3f, %+7.3f, %+7.3f] m   rpy=[%+7.1f, %+7.1f, %+7.1f] deg" % (
        d[0], d[1], d[2], d[3]*57.3, d[4]*57.3, d[5]*57.3)

def fmt_joints(j):
    return "[" + ", ".join("%+7.1f" % (x*57.3) for x in j) + "] deg"

def run_test():
    rospy.init_node('coord_diag')
    side = rospy.get_param('~side', 'right')
    diag = CoordDiagnostic(side)
    arm_name = '右臂' if side == 'right' else '左臂'

    def banner(title):
        print("\n" + "=" * 68)
        print("  %s" % title)
        print("=" * 68)

    def sep():
        print("-" * 68)

    banner("坐标系映射诊断 — %s" % arm_name)
    print()
    print("【实验目的】")
    print("  逐轴测试 VR 手柄运动与机械臂末端运动的对应关系，检查坐标系映射是否正确。")
    print()
    print("【准备工作】")
    print("  1. 在终端1 roslaunch oculus_reader teleop_double_piper.launch")
    print("  2. 按 %s 归位机械臂到预设中间姿态" % ('A键(右臂)' if side == 'right' else 'X键(左臂)'))
    print("  3. 将 VR 手柄放在身前自然舒适位置（肘部高度，正对前方）")
    print("  4. 按 %s 使能手柄控制" % ('B键(右臂)' if side == 'right' else 'Y键(左臂)'))
    print()
    print("【测试要点】")
    print("  - 每次只做单一方向的动作，幅度尽量大（10-20cm 或 30-60°）")
    print("  - 做完动作后让机械臂回到原位附近，再按 Enter 记录")
    print("  - 仔细观察机械臂末端（手腕/夹爪处）实际向哪个方向移动/旋转")
    print("  - 如果机械臂失能、抖动、或明显方向不对，请备注")
    print()

    input(">>> 按 Enter 开始标定基准...")

    for i in range(10):
        if diag.calibrate():
            print("  [OK] 基准已记录")
            break
        rospy.sleep(0.1)
    else:
        print("  [FAIL] 无法获取 VR 位姿，请检查手柄连接")
        return

    # ==================== 测试定义 ====================
    # (编号, 名称, VR动作说明, 期望末端运动, 观测提示)
    tests = [
        # ---- 平移 ----
        ("X+", "前推",
         "手柄向前推（远离身体，水平方向）",
         "机械臂末端应向前方伸展远离身体",
         "末端是否向前移动？还是向其他方向？"),

        ("X-", "后拉",
         "手柄向后拉（靠近胸口，水平方向）",
         "机械臂末端应向后方收缩靠近身体",
         "末端是否向后移动？"),

        ("Y+", "上抬",
         "手柄竖直向上抬（向天花板）",
         "机械臂末端应向上方移动",
         "末端是否向上移动？"),

        ("Y-", "下压",
         "手柄竖直向下压（向地面）",
         "机械臂末端应向下方移动",
         "末端是否向下移动？"),

        ("Z+", "右移",
         "手柄水平向右平移",
         "机械臂末端应向右方移动",
         "末端是否向右移动？（注意：左臂和右臂的'右'方向不同）"),

        ("Z-", "左移",
         "手柄水平向左平移",
         "机械臂末端应向左方移动",
         "末端是否向左移动？"),

        # ---- 旋转 ----
        ("Roll+", "右旋(顺拧)",
         "手柄绕自身长轴顺时针拧转（像拧螺丝/拧门把手）",
         "机械臂末端应绕自身X轴（手臂指向方向）正转",
         "末端绕手臂指向方向旋转？顺时针还是逆时针？"),

        ("Roll-", "左旋(逆拧)",
         "手柄绕自身长轴逆时针拧转",
         "机械臂末端应绕自身X轴反转",
         "末端绕手臂指向方向旋转方向？"),

        ("Pitch+", "抬头(前倾)",
         "手柄顶部向前倾倒（像飞机推杆低头）",
         "机械臂末端应绕自身Y轴正转（末端上翘）",
         "末端是上翘还是下压？"),

        ("Pitch-", "低头(后倾)",
         "手柄顶部向后倾倒（像飞机拉杆抬头）",
         "机械臂末端应绕自身Y轴反转（末端下压）",
         "末端是下压还是上翘？"),

        ("Yaw+", "右转(水平)",
         "手柄水平向右旋转（保持水平，向右转）",
         "机械臂末端应绕自身Z轴正转（末端右转）",
         "末端是否向右旋转？"),

        ("Yaw-", "左转(水平)",
         "手柄水平向左旋转（保持水平，向左转）",
         "机械臂末端应绕自身Z轴反转（末端左转）",
         "末端是否向左旋转？"),
    ]

    # ==================== 逐项测试 ====================
    results = []

    for idx, (axis, name, vr_action, expected, hint) in enumerate(tests):
        banner("[%d/%d] %s — %s" % (idx+1, len(tests), axis, name))

        print()
        print("  【VR 手柄动作】")
        print("    %s" % vr_action)
        print()
        print("  【理论期望】")
        print("    %s" % expected)
        print()
        print("  【操作步骤】")
        print("    1. 按住使能按钮 (B/Y)")
        print("    2. 只做'%s'这一个动作，幅度尽量大" % name)
        print("    3. 松开使能按钮，让机械臂停在终点附近")
        print("    4. 按 Enter 记录 VR 数据")
        print()

        input(">>> 完成'%s'动作后按 Enter..." % name)

        delta = diag.get_delta()
        joints = diag.get_joints()

        sep()
        print("  [VR 增量数据]")
        if delta:
            print("    %s" % fmt_delta(delta))
            # 分析主要变化轴
            pos_mag = [abs(delta[0]), abs(delta[1]), abs(delta[2])]
            rot_mag = [abs(delta[3]), abs(delta[4]), abs(delta[5])]
            pos_axes = ["X", "Y", "Z"]
            rot_axes = ["Roll", "Pitch", "Yaw"]
            max_pos = pos_axes[pos_mag.index(max(pos_mag))]
            max_rot = rot_axes[rot_mag.index(max(rot_mag))]
            print("    主要平移轴: %s (|dx|=%5.3f  |dy|=%5.3f  |dz|=%5.3f)" % (
                max_pos, delta[0], delta[1], delta[2]))
            print("    主要旋转轴: %s (|dr|=%4.1f  |dp|=%4.1f  |dy|=%4.1f deg)" % (
                max_rot, abs(delta[3])*57.3, abs(delta[4])*57.3, abs(delta[5])*57.3))
        else:
            print("    (无数据)")
        print()
        if joints:
            print("  [关节角度]")
            print("    %s" % fmt_joints(joints))
        print()

        # ===== 用户输入观测结果 =====
        print("  【请输入机械臂实际观测】")
        obs = input("  >>> 机械臂末端实际向哪个方向移动/旋转了？: ").strip()
        notes = input("  >>> 备注 (失能/抖动/异常等, 无则回车): ").strip()

        results.append({
            "test": "%s %s" % (axis, name),
            "vr_delta": delta,
            "joints": joints,
            "observation": obs if obs else "(未填写)",
            "notes": notes,
        })

        print()

    # ==================== 最终汇总 ====================
    banner("测试汇总报告 — %s" % arm_name)
    print()
    print("  %-20s %-30s %s" % ("测试项", "VR 增量 (主要分量)", "实际末端运动"))
    print("  " + "-" * 65)
    for r in results:
        d = r['vr_delta']
        if d:
            pos_max = max(range(3), key=lambda i: abs(d[i]))
            rot_max = max(range(3,6), key=lambda i: abs(d[i]))
            pos_str = "%s=%+.3fm" % (["X","Y","Z"][pos_max], d[pos_max])
            rot_str = "%s=%+.1f°" % (["R","P","Y"][rot_max-3], d[rot_max]*57.3)
            vr_str = "%s  %s" % (pos_str, rot_str)
        else:
            vr_str = "(无数据)"

        print("  %-20s %-30s %s" % (r['test'], vr_str, r['observation']))
        if r['notes']:
            print("  %-20s %s" % ("", "[备注] " + r['notes']))

    # ==================== 保存文件 ====================
    save_results = []
    for r in results:
        d = r['vr_delta']
        save_results.append({
            "test": r['test'],
            "vr_delta": d,
            "joints_deg": [j*57.3 for j in r['joints']] if r['joints'] else None,
            "observation": r['observation'],
            "notes": r['notes'],
        })

    fname = "/tmp/coord_result_%s_%s.json" % (side, datetime.now().strftime("%H%M%S"))
    with open(fname, 'w') as f:
        json.dump(save_results, f, indent=2, ensure_ascii=False)
    print("\n  结果已保存到: %s" % fname)

    print()
    print("  请把上面的汇总表发给我，我做坐标系映射分析。")

if __name__ == '__main__':
    run_test()
