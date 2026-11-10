# ROS Node Audit

## Observed live system

At 11:05–11:07 CST, a pre-existing experiment was running a private ROS Master on `127.0.0.1:11312`. Its launch command was:

`roslaunch yuanyou2 three_cameras.launch start_head:=true start_left_wrist:=true start_right_wrist:=true right_wrist_align_depth:=false`

This audit did not start that launch.

Observed nodes:

- `/head_camera/usb_cam`
- `/left_wrist_d435/realsense2_camera`
- `/left_wrist_d435/realsense2_camera_manager`
- `/right_wrist_d435/realsense2_camera`
- `/right_wrist_d435/realsense2_camera_manager`
- `/camera_diagnostic`
- `/ab_probe_31125_1791860760263`
- `/rosout`

Observed image and camera-info topics:

- Head RGB: `/head_camera/usb_cam/image_raw`
- Head camera info: `/head_camera/usb_cam/camera_info`
- Left RGB: `/left_wrist_d435/color/image_raw2`
- Left raw depth: `/left_wrist_d435/depth/image_rect_raw2`
- Left RGB camera info: `/left_wrist_d435/color/camera_info`
- Left depth camera info: `/left_wrist_d435/depth/camera_info`
- Right RGB: `/right_wrist_d435/color/image_raw2`
- Right raw depth: `/right_wrist_d435/depth/image_rect_raw2`
- Right RGB camera info: `/right_wrist_d435/color/camera_info`
- Right depth camera info: `/right_wrist_d435/depth/camera_info`

The two image topics checked before shutdown had a single expected publisher each. No duplicate camera publisher or duplicate node-name conflict was observed. The RealSense image publishers were their respective namespaced nodelet managers, which is expected nodelet behavior.

## State transitions during audit

The pre-existing 60-second diagnostic run ended and shut down its own launch and Master while read-only topic inspection was in progress. At that point, `rostopic` and `rosnode` could not communicate with the Master.

Before report completion, external automation started `experiment_B_rerun`. At the final 11:12:12 check:

- ROS Master 11312: online
- All five camera nodes listed above: online
- Principal image/camera-info topics: not yet visible in the immediate startup snapshot, so stream readiness at that exact instant was still initializing

Per the task constraints, this audit did not start, stop, or restart any launch or node.

## Warnings from the existing run

- ROS log directory usage exceeded 1 GB.
- Head camera calibration file `~/.ros/camera_info/usb_cam.yaml` was absent.
- RealSense wrapper warned that runtime librealsense differed from its compile-time version.
- A `Left MIPI error` hardware notification occurred once. Interleaved dual-camera logs do not identify its device conclusively.
- Both RealSense dynamic-reconfigure namespaces reported an unsupported `power_line_frequency=3` value.
- No kernel USB reset/disconnect/descriptor/timeout error was found in the read-only `dmesg` filter.
