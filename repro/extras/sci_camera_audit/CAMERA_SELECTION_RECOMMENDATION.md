# Camera Selection Recommendation for Stage04.7

## Recommendation

**Provisional choice: right-wrist D435, serial `317422072133`.**

Rationale:

- It is unambiguously bound to the right namespace and USB path `2-1.1.1`.
- Its 60-second RGB stream delivered 1800 frames at 29.98 FPS with no observed drops, stalls, duplicate stamps, or timestamp regression.
- Its installed firmware (`5.17.0.10`) is newer than the left camera firmware (`5.13.0.55`), although the local tool reports `5.16.0.1` as its recommended version; no firmware action is authorized or recommended during this audit.

This is not yet an unconditional Stage04.7 readiness decision. Before scientific static depth measurement, perform an explicitly authorized, short raw-depth validation on the selected device and capture:

1. actual ROS depth encoding and `frame_id` from a live message;
2. depth units/scale from the live driver/device;
3. raw-depth FPS, sequence gaps, and timestamp monotonicity;
4. zero/invalid/saturated pixel ratios and representative distance statistics;
5. attribution or recurrence check for the observed `Left MIPI error`;
6. confirmation that the intended camera-info calibration is loaded.

Do not silently update firmware, EEPROM, calibration, ROS wrapper, or librealsense as part of that validation. Any such change needs a separate controlled compatibility plan.

## Why the left D435 is not the first provisional choice

The left camera's RGB stream was equally stable, but its firmware is older than the local recommended version and the requested concern about left raw-depth abnormal values could not be resolved by this RGB-only run. This does not prove the left camera is faulty.

## Blocking issues

- At completion time an externally initiated rerun had the Master and camera nodes online, but the image topics were still initializing in the immediate snapshot; readiness must be reconfirmed at the authorized Stage04.7 precheck.
- Raw-depth frame rate and pixel validity were not measured for either D435.
- Depth scale was not verified.
- A single un-attributed RealSense `Left MIPI error` requires a controlled recurrence check.
- Runtime/compile-time librealsense mismatch warning should be documented and assessed before locking the experimental software baseline.
