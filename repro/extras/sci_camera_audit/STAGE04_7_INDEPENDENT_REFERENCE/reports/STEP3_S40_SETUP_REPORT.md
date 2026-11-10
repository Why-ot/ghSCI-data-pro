# STAGE04.7 Step3 S40 Physical Reference Setup Report

```text
S40_TARGET_PHYSICALLY_BUILT = UNVERIFIED
S40_REFERENCE_HEIGHT = NOT_MEASURED
REFERENCE_MEASUREMENT_ROWS = 15
REFERENCE_U95 = UNVERIFIED
CAMERA_STREAM = NOT_STARTED
ROBOT_MOTION = NO
PROTOCOL_FROZEN = NO
READY_FOR_PHYSICAL_MEASUREMENT = CONDITIONAL
READY_FOR_150_FRAME_PILOT = NO
```

## Input-file audit

All required inputs were found:

- `protocol/PROTOCOL_FREEZE_v1.0.md`
- `protocol/PROTOCOL_v1.0_REVISED_CANDIDATE.md`
- `reports/STEP2A_PREPARATION/STEP2A_EXECUTIVE_REPORT.md`
- `reports/STEP2B_FIRST_STREAM/STEP2B_EXECUTIVE_REPORT.md`
- `reference_measurements/S40_MEASUREMENT_ENTRY.csv`
- `reference_measurements/S40_600MM_CENTER_PILOT_CHECKLIST.md`
- `EXPERIMENT_MANIFEST.csv`

Confirmed evidence from the existing records:

- `RIGHT_D435_SERIAL = 317422072133`
- Actual Depth profile: `848x480 Z16 30FPS`
- Active depth scale: `0.001 m/raw_unit`
- `STEP2B_CAPTURE = PASS`
- Step2B camera resource release: `YES`
- Formal experiment frames: `0`

## Created or reused preparation artifacts

- Created `reference_measurements/S40_SETUP_GUIDE.md`.
- Reused and schema-adjusted `reference_measurements/S40_MEASUREMENT_ENTRY.csv` only after confirming all existing measurement values were blank. It contains 15 records: five positions × three independent repositioned measurements.
- Created `reference_measurements/REFERENCE_UNCERTAINTY_WORKSHEET.csv` with no numerical uncertainty values.
- Reused `reference_measurements/S40_600MM_CENTER_PILOT_CHECKLIST.md` as the first pilot operation card because it already specifies S40, nominal 600 mm, CENTER, five independent placements, 30 frames per placement, independent records, and the non-independence of within-placement frames.

No actual height, instrument accuracy, uncertainty, physical construction state, ROI, or pilot result was generated.

## Uncertainty evidence classification

The worksheet uses `evidence_basis` to distinguish:

- `MEASURED_VALUE`: directly measured with documented method.
- `MANUFACTURER_SPECIFICATION`: traceable manufacturer or calibration information.
- `REASONABLE_ESTIMATE`: justified estimate with assumptions and source.
- `UNKNOWN`: no defensible value currently available.

All initial rows are `UNKNOWN`. No combined uncertainty or `U95` was calculated.

## Scientific-condition review

| ID | Question | Current result | Finding |
|---|---|---|---|
| A | Can the true normal separation of the two reference planes be measured? | `CONDITIONAL` | The guide defines an admissible caliper method, but the physical target, access to the correct surfaces, contact geometry, and parallelism have not been inspected. |
| B | Can the camera simultaneously see both planes? | `UNVERIFIED` | The target design requires simultaneous Depth visibility, but no camera stream or physical view check was performed in this task. |
| C | Can pose affect comparison between Z difference and true height? | `YES` | Tilt and spatially separated ROIs can change camera-axis Z independently of normal separation. A fronto-parallel tolerance or reviewed 3D correction is required. |
| D | Can ROIs avoid the step edge? | `CONDITIONAL` | The target is required to provide sufficient interior areas, but final Depth-coordinate ROIs have not been defined or inspected. |
| E | Could the reference method miss systematic bias? | `YES_OR_UNKNOWN` | Instrument accuracy, calibration, flatness, parallelism, fixture deformation, contact force, alignment, temperature, and surface definition remain potential sources. |
| F | Does the current apparatus support per-pixel ground truth? | `NO_CURRENT_EVIDENCE` | The planned physical method supports an overall step-geometry reference. It does not establish spatially registered per-pixel ground truth. |

## Readiness decision

`READY_FOR_PHYSICAL_MEASUREMENT = CONDITIONAL` because the documentation and blank worksheets are ready, but an on-site person must confirm the target exists, correct reference surfaces are accessible, a suitable instrument is available, the fixture is stable, and the method is safe.

`READY_FOR_150_FRAME_PILOT = NO` because S40 has not been physically verified or measured, `REFERENCE_U95` remains unverified, final Depth ROIs and geometric tolerances are absent, and a fresh safety confirmation and explicit acquisition authorization have not been provided.

## Scope and integrity declaration

- Original protocol status remains draft.
- Revised candidate remains `NOT_FROZEN`.
- No protocol or experiment-manifest result was changed.
- Camera stream started: `NO`.
- ROS started: `NO`.
- Robot/CAN/gripper command sent: `NO`.
- Physical target construction asserted: `NO`.
- Physical measurement performed: `NO`.
- Stage05 started: `NO`.
