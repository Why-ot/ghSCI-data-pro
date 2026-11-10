# Raw Depth Stream Audit

Audit time: 2026-10-13, Asia/Shanghai

## Outcome

**STOPPED — existing ROS Master and camera nodes were not accessible.**

The requested safety stop condition was met before topic discovery or subscription:

- The initial remote command environment had `ROS_MASTER_URI` unset.
- After sourcing only `/opt/ros/noetic/setup.bash` to make ROS CLI tools available, the unchanged default resolved as `http://localhost:11311`.
- `rosnode list` returned `ERROR: Unable to communicate with master!` (exit 1).
- `rostopic list` returned `ERROR: Unable to communicate with master!` (exit 1).
- No listener existed on TCP port 11311 or 11312.
- No `roscore`, `rosmaster`, camera `roslaunch`, `realsense2_camera`, or `usb_cam_node` process was running.
- `lsusb` still showed two Intel devices `8086:0b07`, but USB enumeration alone cannot establish ROS stream availability or namespace ownership.

No ROS Master URI was exported or persisted, no Master or launch was started, and no 30-second subscriber was run.

## Historical values read from the prior audit — not revalidated

- Expected left D435 serial: `342222072464`
- Expected right D435 serial: `317422072133`
- Historical left raw-depth topic: `/left_wrist_d435/depth/image_rect_raw2`
- Historical right raw-depth topic: `/right_wrist_d435/depth/image_rect_raw2`

These topic names and bindings are marked **UNVERIFIED** for the present precheck because the current Master was unavailable. They were not used for subscription.

## Actions explicitly not performed

No camera launch, roscore, ROS node, publisher, robot-control process, CAN/Piper/VR operation, USB reset, parameter change, SDK/firmware change, Stage04.7 collection, or Stage05 work was performed.
