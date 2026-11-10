# STEP2 SDK Runtime Audit

## Native runtime

| Item | Result |
|---|---|
| `rs-enumerate-devices` | `/usr/local/bin/rs-enumerate-devices` |
| CLI version | `2.55.1.0` |
| Runtime library loaded by CLI | `/usr/local/lib/librealsense2.so.2.55` |
| Resolved library file | `/usr/local/lib/librealsense2.so.2.55.1` |
| Architecture | `aarch64` |
| USB backend dependency | `/lib/aarch64-linux-gnu/libusb-1.0.so.0` |
| udev dependency | `/lib/aarch64-linux-gnu/libudev.so.1` |

## Python binding

- Python executable: `/usr/bin/python3`
- Python version: `3.8.10`
- `pyrealsense2`: `NOT_FOUND`
- Installation attempted: `NO`

The native SDK remains usable for enumeration and calibration metadata. No package was installed, upgraded, rebuilt, or reconfigured.

## Known version difference

- Direct `/usr/local` runtime: librealsense `2.55.1`
- ROS Debian package: `ros-noetic-librealsense2 2.50.0`
- ROS RealSense wrapper: `ros-noetic-realsense2-camera 2.3.2`

STEP2 used the direct `/usr/local` SDK tool. No ROS environment or package was modified.

## Pre-stream state checks

| Check | Result |
|---|---|
| ROS master listener on 11311/11312/11325 | None detected |
| `ROS_MASTER_URI` | Empty/unset |
| Existing RealSense/camera capture process | None detected |
| `/dev/video*` consumers reported by `fuser` | None detected |
| Robot/Piper/controller/gripper process | None detected |
| Robot control API called | NO |
| CAN command sent | NO |
| USB path | 5 Gbps topology; camera descriptor 3.2 |

Remote process checks cannot prove that a wrist-mounted camera and robot are physically secured. Static mounting safety therefore remains `UNVERIFIED` pending an authorized human check.

## FAILED_GATE

1. Protocol scientific review returned `ISSUES_FOUND` (`PRI-001`, `PRI-002`).
2. Physical static-fix safety of the wrist-mounted camera could not be confirmed remotely.
3. `pyrealsense2` is unavailable, although the native SDK is present; no installation is authorized.

The first two conditions independently prevent the 20-second stream test under the task's all-gates-pass rule. No attempt was made to terminate other processes, start ROS, or start a camera pipeline.
