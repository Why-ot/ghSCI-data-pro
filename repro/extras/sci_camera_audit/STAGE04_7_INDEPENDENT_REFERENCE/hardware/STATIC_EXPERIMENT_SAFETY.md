# STAGE04.7 Static Experiment Safety Checklist

Status: `MANDATORY_BEFORE_ANY_PHYSICAL_EXPERIMENT`

## Prohibited actions

- The robot arm must not move during this stage.
- Robot joint motion must not be used to adjust camera viewpoint.
- No automatic or manual software command may enable or disable the robot arm.
- No trajectory, servo, jog, gripper, CAN, or Piper command is permitted.

## Physical adjustment rule

Any wrist-camera installation or adjustment must be performed by personnel only after the equipment has been placed in a confirmed safe state under the laboratory's approved safety procedure. Software inactivity alone is not proof of a safe physical state.

Before any person touches or adjusts the wrist camera, independently confirm:

- The robot cannot move unexpectedly.
- Stored or gravitational energy is controlled.
- The camera and target can be adjusted without entering a hazardous region.
- Cables and mounts are secure and cannot pull the robot or target.
- The static mounting will remain stable for all planned repeats.

If the wrist camera cannot be confirmed as safely and statically fixed, pause the physical experiment. Do not compensate by commanding robot motion.

## STEP1 declaration

STEP1 materializes documentation only. It authorizes no physical adjustment, camera capture, ROS startup, robot enable/disable action, or movement.
