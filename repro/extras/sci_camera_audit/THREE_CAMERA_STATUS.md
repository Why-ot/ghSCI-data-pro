# Three-Camera Status

## Device identification

| Camera | Device identity | USB attachment | ROS identity |
|---|---|---|---|
| Head | Orbbec DaBai DCW2 RGB, USB serial `AUISA3P001W` | USB path `1-2.1.2.3`, USB 2.0/480 Mb/s, `/dev/video12` | `/head_camera/usb_cam` |
| Left wrist | Intel RealSense D435, librealsense serial `342222072464`, ASIC/USB serial `422543021422`, FW `5.13.0.55` | USB path `2-1.1.3`, 5 Gb/s (reported by wrapper as USB 3.2), video base `/dev/video6` | `/left_wrist_d435/*` |
| Right wrist | Intel RealSense D435, librealsense serial `317422072133`, ASIC/USB serial `327643020576`, FW `5.17.0.10` | USB path `2-1.1.1`, 5 Gb/s (reported by wrapper as USB 3.2), video base `/dev/video0` | `/right_wrist_d435/*` |

The left and right cameras are conclusively different physical D435 devices: both the librealsense serials and USB physical paths differ.

## Stream properties observed/configured

| Camera | RGB | Raw depth | Camera info | Encoding | frame_id |
|---|---|---|---|---|---|
| Head | `/head_camera/usb_cam/image_raw` | Not published | `/head_camera/usb_cam/camera_info` | RGB `rgb8` | `head_camera` |
| Left | `/left_wrist_d435/color/image_raw2` | `/left_wrist_d435/depth/image_rect_raw2` | color and depth camera-info topics listed above | RGB `rgb8`; depth configured/logged as `Z16` (ROS convention normally `16UC1`, but message header was not captured before shutdown) | color `left_wrist_d435_color_optical_frame`; depth `left_wrist_d435_depth_optical_frame` |
| Right | `/right_wrist_d435/color/image_raw2` | `/right_wrist_d435/depth/image_rect_raw2` | color and depth camera-info topics listed above | RGB `rgb8`; depth configured/logged as `Z16` (ROS convention normally `16UC1`, but message header was not captured before shutdown) | color `right_wrist_d435_color_optical_frame`; depth `right_wrist_d435_depth_optical_frame` |

All configured image sizes were 640x480 at 30 FPS. `align_depth=false` was in effect for both D435 devices, so the named `image_rect_raw2` topics are the appropriate raw depth streams.

Depth scale was not exposed in the captured ROS parameters or read-only device summary and was not inferred. It remains **NOT VERIFIED**.

## Passive 60-second RGB observation

These measurements were produced by the pre-existing diagnostic process while all three cameras were connected concurrently:

| Camera | Frames | Actual FPS | Drops | Stalls | Timestamp regressions | Duplicate stamps |
|---|---:|---:|---:|---:|---:|---:|
| Head | 1784 | 29.71 | 2 | 0 | 0 | 0 |
| Left wrist RGB | 1800 | 29.98 | 0 | 0 | 0 | 0 |
| Right wrist RGB | 1800 | 29.98 | 0 | 0 | 0 | 0 |

All RGB streams were resolution-consistent at 640x480. Timestamps used the same clock; median measured latency was approximately 3.6 ms (head), 41.0 ms (left), and 40.7 ms (right). This run provides no evidence of severe right-wrist RGB dropping.

## Anomaly assessment

- Left-wrist abnormal depth values: **NOT TESTED**. Raw depth was advertised, but the existing diagnostic subscribed only to RGB and did not retain depth pixel statistics.
- Right-wrist severe drop: **not observed for RGB** in the 60-second run; raw-depth drop behavior remains unverified.
- Three-camera simultaneous connection: **PASS for RGB connectivity and throughput** during the run. Concurrent raw-depth quality/throughput was not measured.
- USB connection: both D435 devices enumerated at 5 Gb/s; no obvious kernel USB reset/disconnect error was found.
- Hardware notification: one `Left MIPI error` appeared in interleaved RealSense logs; attribution to a specific D435 is unresolved.
- Completion-time status (11:12:12): external `experiment_B_rerun` had brought the Master and all five camera nodes online again; principal image topics were not yet visible in that immediate startup snapshot. The audit did not start this rerun.
