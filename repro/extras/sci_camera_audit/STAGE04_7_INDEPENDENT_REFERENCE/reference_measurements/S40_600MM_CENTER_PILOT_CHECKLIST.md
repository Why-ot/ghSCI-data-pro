# S40 600 mm Center Pilot Checklist

## Scope

- Pilot configuration: `S40_600MM_CENTER`
- Planned independent placements: `5`
- Planned frames per placement: `30`
- Current state: `NOT_STARTED`
- Formal experiment authorization from this checklist: `NO`

The previous Step2B safety confirmation and 20-second stream authorization do not automatically apply to this new physical experiment. Obtain a fresh on-site safety confirmation and separate user authorization before starting any camera stream.

## A. Safety and static setup gate

| Check | Initial state | On-site record |
|---|---|---|
| Robot is safely and stably parked | `NOT_CONFIRMED` |  |
| Mechanical arm will not move during setup or capture | `NOT_CONFIRMED` |  |
| RIGHT D435 mounting remains secure | `NOT_CONFIRMED` |  |
| No robot joint motion is needed to adjust viewpoint | `NOT_CONFIRMED` |  |
| USB and power connections are safe | `NOT_CONFIRMED` |  |
| Experiment area is clear of collision/pinch hazards | `NOT_CONFIRMED` |  |
| On-site responsible person and time recorded | `NOT_CONFIRMED` |  |

If any item is not confirmed, stop. Do not use robot movement to obtain the desired view.

## B. Target and distance setup

- [ ] Use the physically measured S40 target; do not substitute nominal `40 mm` for `h_ref`.
- [ ] Fix the camera without movement throughout the pilot.
- [ ] Place the target at the nominal `600 mm` configuration.
- [ ] Record the actual setup distance: `________________ mm`.
- [ ] Record the distance measurement instrument: `________________`.
- [ ] Record the camera and target reference points used for distance: `________________`.
- [ ] Place the target in the image center without moving the robot.
- [ ] Confirm both reference planes appear in the Depth field of view.
- [ ] Record target-plane parallelism/flatness evidence or `UNKNOWN`.
- [ ] Record the target normal relative to the camera optical axis.
- [ ] Record the measured or estimated inclination and method; do not assume fronto-parallel geometry.

## C. ROI definition gate

The primary raw-depth ROIs must be defined in the Depth image coordinate system. RGB pixel coordinates must not be copied directly into the Depth image unless a reviewed intrinsics/extrinsics projection has been performed. No depth-color alignment is permitted for the primary raw-depth stream.

For each of the two reference-plane ROIs:

- [ ] Record Depth-image ROI coordinates, size, and selection rule.
- [ ] Keep the ROI away from the step edge, occlusion boundary, mixed pixels, holes, and damaged surface regions.
- [ ] Confirm the ROI corresponds to the intended physical reference plane.
- [ ] Record the positive-valid depth ratio separately for plane A and plane B.
- [ ] Record zero fraction separately for plane A and plane B.
- [ ] Check and record whether raw saturated values (`65535` for the observed Z16 chain) occur inside either ROI.
- [ ] Do not interpret positive-valid ratio as geometric correctness.

Proposed ROI record, pending review:

| Plane | Depth ROI `(x,y,width,height)` | Selection rationale | Valid ratio | Zero fraction | Saturation count | Status |
|---|---|---|---:|---:|---:|---|
| A |  |  |  |  |  | `NOT_DEFINED` |
| B |  |  |  |  |  | `NOT_DEFINED` |

## D. Independent-placement execution plan

Each row is one independently re-established physical placement and therefore one experimental unit. Its 30 frames form a within-placement time series, not 30 independent experiments.

| Placement/repeat | Target removed and independently replaced | Actual distance recorded | Pose/inclination recorded | Plane A ROI metrics recorded | Plane B ROI metrics recorded | Planned frames | Actual frames | Independent record ID | Status |
|---:|---|---|---|---|---|---:|---:|---|---|
| 1 | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | 30 |  | `S47-S40-D0600-CENTER-R01` | `PLANNED` |
| 2 | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | 30 |  | `S47-S40-D0600-CENTER-R02` | `PLANNED` |
| 3 | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | 30 |  | `S47-S40-D0600-CENTER-R03` | `PLANNED` |
| 4 | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | 30 |  | `S47-S40-D0600-CENTER-R04` | `PLANNED` |
| 5 | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | `NOT_DONE` | 30 |  | `S47-S40-D0600-CENTER-R05` | `PLANNED` |

Do not overwrite one placement with another. Invalid or incomplete attempts require a retained record and documented reason. This checklist does not start the pilot or mark any manifest record as captured.
