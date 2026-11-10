# STAGE04.7 STEP2 Right D435 SDK Precheck — Executive Report

## Required output

```text
PROTOCOL_SCIENTIFIC_REVIEW = ISSUES_FOUND
RIGHT_D435_DETECTED = YES
RIGHT_D435_SERIAL = 317422072133
SDK_CAPTURE_STATUS = NOT_STARTED
REQUESTED_DEPTH_PROFILE_SUPPORTED = YES
ACTUAL_DEPTH_PROFILE = NOT_STARTED
ACTUAL_RGB_PROFILE = NOT_STARTED
DEPTH_SCALE = UNVERIFIED
DEPTH_INTRINSICS = PASS
DEPTH_COLOR_EXTRINSICS = PASS
ACTUAL_DEPTH_FPS = NOT_MEASURED
VALID_DEPTH_RATIO = NOT_MEASURED
TIMESTAMP_STATUS = UNVERIFIED
CAMERA_RESOURCE_RELEASED = YES
READY_FOR_STATIC_MEASUREMENT = NO
PROTOCOL_STATUS = DRAFT_RECONSTRUCTED_PENDING_USER_SIGNOFF
FORMAL_EXPERIMENT_FRAMES = 0
ROBOT_MOVEMENT = NO
STAGE05_STARTED = NO
```

## Executive finding

The specified RIGHT D435 is currently enumerated with the correct serial over a 5 Gbps USB topology. The requested depth and compatible color modes are both advertised by the device, and calibration metadata for the requested resolutions is readable. The direct native SDK resolves to librealsense 2.55.1; `pyrealsense2` is absent, and the known ROS Debian librealsense 2.50.0 remains installed but unused.

The 20-second diagnostic stream was deliberately not started. Two required scientific statements are absent from the draft protocol, and the static physical safety of the wrist-mounted camera cannot be confirmed remotely. Under the explicit all-preconditions-pass rule, these are failed gates rather than reasons to bypass the protocol.

No depth frames were received or converted to millimetres. Therefore actual running profiles, actual FPS, timestamps, continuity, valid-depth ratio, distribution metrics, and current depth scale remain unverified. The SDK-advertised Depth Units default of `0.001 m/unit` is recorded only as a default and is not claimed as the actual current scale.

## FAILED_GATE

- `PRI-001`: Uncertainty layers are not explicitly distinguished.
- `PRI-002`: The 30-frame repeated-observation/non-independent-unit rule is not explicit.
- `SAFETY-001`: Static physical security of the wrist-mounted camera and robot is not remotely verified.

## Required disposition before another SDK capture attempt

1. User reviews the two protocol issues and authorizes any protocol revision; STEP2 did not edit the protocol.
2. Protocol remains draft until explicit user sign-off and must not be auto-frozen.
3. An authorized person confirms the wrist camera and robot are safely static without commanding robot motion.
4. A separately authorized rerun may then perform the single 20-second target-serial SDK test using the already-supported profiles.

This task stopped without entering physical target acquisition, formal 135-record capture, protocol freezing, robot control, or Stage05.
