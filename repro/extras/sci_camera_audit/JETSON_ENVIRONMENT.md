# Jetson Remote Environment Audit

Audit time: 2026-10-13 11:05–11:08 CST (Asia/Shanghai)

## Host and SSH

| Item | Observed value | Result |
|---|---|---|
| hostname | `yuanyou` | PASS |
| user | `yuanyou` | PASS |
| SSH | `192.168.31.10:64894 -> 192.168.31.230:22` | PASS |
| kernel | `Linux 5.10.216-tegra`, aarch64 | PASS (Jetson/Tegra) |
| OS | Ubuntu 20.04.6 LTS (focal) | PASS |
| ROS install | `/opt/ros/noetic` exists | PASS |
| workspace | `/home/yuanyou/yuanyou2_ws` exists | PASS |

`/opt/ros/noetic/setup.bash` and `~/rgbd_grasp_research_ws/devel/setup.bash` are sourced by `.bashrc`, but the non-interactive audit shell initially had no ROS executables in `PATH`. The audit sourced only `/opt/ros/noetic/setup.bash` locally for read-only commands; no configuration file was changed.

## ROS network environment

Initial audit shell:

- `ROS_MASTER_URI`: unset
- `ROS_IP`: unset
- `ROS_HOSTNAME`: unset

The already-running camera processes had:

- `ROS_MASTER_URI=http://127.0.0.1:11312`
- `ROS_IP=127.0.0.1`
- `ROS_HOSTNAME=127.0.0.1`

The audit pointed its read-only ROS clients to that existing Master. It did not start, stop, or alter a ROS Master. The pre-existing experiment shut down its own Master at approximately 11:07. External automation then started `experiment_B_rerun`; at completion-time check (11:12:12), its Master on 11312 and the five camera nodes were online again. The audit neither caused nor controlled either transition.

## Safety statement

No robot-control command, publisher, launch, motor/CAN operation, camera setting, EEPROM operation, calibration change, or restart was performed. Only read-only inspection and passive subscriptions associated with the already-running experiment were used.
