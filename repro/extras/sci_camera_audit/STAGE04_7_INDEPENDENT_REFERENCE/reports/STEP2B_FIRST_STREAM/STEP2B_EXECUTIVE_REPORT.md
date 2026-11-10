# STAGE04.7 STEP2B First Raw RGB-D Stream — Executive Report

```text
STEP2A_GATE = PASS
PHYSICAL_SAFETY_CONFIRMED = YES
RIGHT_D435_SERIAL = 317422072133
SDK_CAPTURE_STATUS = PASS
DEPTH_PROFILE = 848x480 Z16 30FPS
COLOR_PROFILE = 640x480 RGB8 30FPS
DEPTH_SCALE = 0.001 m/raw_unit (1.0 mm/raw_unit)
DEPTH_FPS = 29.9981871514
RGB_FPS = 29.9981864179
VALID_DEPTH_RATIO = 0.740843328256
TIMESTAMP_STATUS = PASS
CAMERA_RESOURCE_RELEASED = YES
READY_FOR_S40_PHYSICAL_EXPERIMENT = CONDITIONAL
FORMAL_EXPERIMENT_FRAMES = 0
ROBOT_MOTION = NO
STAGE05_STARTED = NO
```

## Outcome

After explicit human confirmation of all seven physical safety conditions, the already-compiled native librealsense C++ program was executed exactly once. It selected serial `317422072133`, simultaneously enabled the requested depth and color streams, warmed up, observed for 20.016 seconds, stopped its pipeline, and exited successfully.

Both active profiles matched the requests. The diagnostic received 600 depth frames and 600 color frames with no missing frame numbers. Both streams used `Global Time`, did not change timestamp domain, and ran at approximately 29.998 FPS.

The active depth sensor reported a scale of `0.001 m/raw unit`. Across 244,224,000 raw depth samples, 74.0843328256% were positive and 25.9156671744% were zero. These figures describe only the observed stream and do not establish geometric correctness.

## Resource and safety outcome

- Program exit: `PASS`
- Program-reported pipeline release: `YES`
- Post-capture `/dev/video0`–`/dev/video5` users: `NONE`
- ROS master started: `NO`
- Robot/CAN/control command issued: `NO`
- Robot motion: `NO`
- Camera option, firmware, or EEPROM modification: `NO`
- Full image sequence saved: `NO`
- Capture retry: `NO`

## Readiness boundary

`READY_FOR_S40_PHYSICAL_EXPERIMENT = CONDITIONAL` because the first simultaneous raw RGB-D SDK stream succeeded, but the revised protocol candidate is not formally frozen and Step2B did not perform independent physical reference measurement, ROI approval, geometry validation, or uncertainty qualification. A separate user authorization is required before any S40 experiment.

This task did not start formal experiment collection or Stage05 and does not authorize either activity.
