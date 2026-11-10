# STEP2A Capture Safety Review

## Physical confirmation

- Confirmation form: `hardware/PHYSICAL_SAFETY_CONFIRMATION.md`
- Form SHA256: `9978826d71955213071f7bc5215751b9be8e9e3470ed4e4f5264710fab0d14fc`
- Checklist items confirmed: `0 of 8`
- On-site responsible person: `NOT_CONFIRMED`
- Confirmation time: `NOT_CONFIRMED`
- `PHYSICAL_SAFETY_CONFIRMED = NO`

No software, process, ROS, USB, or device-enumeration observation was used as a substitute for human physical confirmation.

## Software capture barriers

1. The executable defaults to no stream.
2. Help and configuration checks exit before SDK context creation.
3. The capture path requires an explicit capture flag and exact authorization token.
4. The target serial is fixed to `317422072133`.
5. The abnormal serial `ffffffffffff` is not named or queried by the program.
6. The program contains no robot-control integration.
7. Maximum observation duration is bounded at 20 seconds.
8. Frame waits have a 5000 ms timeout and pipeline ownership is guarded for release.

## Current state

- Camera stream started: `NO`
- Actual depth frames: `0`
- Formal experiment started: `NO`
- Robot movement: `NO`
- Physical safety confirmed: `NO`

## Preconditions for a future 20-second precheck

- Authorized personnel complete every applicable physical safety checklist item.
- The user reviews the revised protocol candidate and decides whether it may govern the precheck.
- The user separately and explicitly authorizes execution of the guarded capture command.
- No robot motion is used to obtain or adjust the view.
- A fresh read-only process/device-occupancy check finds no conflict.

Until those conditions are met, readiness is `CONDITIONAL` and streaming remains prohibited.
