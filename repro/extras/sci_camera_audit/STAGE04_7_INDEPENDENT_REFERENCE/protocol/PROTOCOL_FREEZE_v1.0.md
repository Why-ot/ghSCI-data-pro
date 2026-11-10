# STAGE04.7 Independent Physical Reference Measurement Protocol

## Document control

- Protocol version: `1.0`
- Protocol status: `DRAFT_RECONSTRUCTED_PENDING_USER_SIGNOFF`
- Historical status: This file was reconstructed for review during STAGE04.7 STEP1. It is not asserted to have existed previously.
- Freeze date: `NOT_ASSIGNED`
- Frozen hash: `NOT_ASSIGNED`
- Change rule: Experimental parameters in this document must not be adjusted in response to later experimental results. Any pre-freeze correction requires explicit user review and a documented revision.

## Scientific objective

Establish an independent physical measurement chain using an Intel RealSense D435 and a caliper/ruler-based physical reference to determine whether positive, syntactically valid depth values can nevertheless be geometrically wrong. The physical reference must remain independent of the D435 depth observations being evaluated.

## Frozen candidate parameters

| Parameter | Value |
|---|---|
| CAMERA | `RIGHT_D435` |
| CAMERA_SERIAL | `317422072133` |
| DEPTH_PROFILE_REQUESTED | `848x480 Z16 30FPS` |
| DEPTH_POSTPROCESSING | `OFF` |
| DISTANCES_MM | `400,600,800` |
| POSITIONS | `CENTER,LEFT,RIGHT` |
| STEP_TARGETS | `S20,S40,S60` |
| REPEATS_PER_CONDITION | `5` |
| FRAMES_PER_REPEAT | `30` |
| TOTAL_CONDITIONS | `27` |
| TOTAL_SETUP_REPEATS | `135` |
| TOTAL_FRAMES_PLANNED | `4050` |
| FIRST_PILOT | `S40_600MM_CENTER` |
| FIRST_PILOT_REPEATS | `5` |

Arithmetic checks:

- `3 step targets x 3 distances x 3 positions = 27 conditions`
- `27 conditions x 5 repeats = 135 setup repeats`
- `135 setup repeats x 30 frames = 4050 planned frames`

No capture is authorized by this STEP1 document. The requested profile must be verified in the later SDK precheck before any physical pilot begins.

## Independent reference measurement rules

For each of `S20`, `S40`, and `S60`:

1. Use at least five explicitly identified physical measurement positions (`P1` through `P5` in the initial sheet).
2. At every position, remove and reposition the caliper before each measurement.
3. Record three independent placements (`1` through `3`) per position.
4. Record target ID, measurement position, repeat number, measured millimetres, operator, caliper model, caliper display resolution, calibration status, and measurement time.
5. Do not pre-populate or infer any measured dimension.
6. Caliper display resolution is not accuracy and is not an expanded uncertainty (`U95`). Accuracy and calibration information must be recorded independently.
7. If an instrument property is not supported by a datasheet, certificate, or inspection, record it as `UNKNOWN`.

Rulers may support setup distance or coarse alignment, but they do not replace the independently documented step-height measurement unless their metrological role is explicitly reviewed.

## Geometric measurand and comparison rule

### Primary measurand

The primary measurand is the relative physical separation between the two step planes, defined as the perpendicular separation of the representative plane surfaces under the reviewed target geometry. It is not automatically the absolute difference between two camera-axis depth coordinates.

### Required geometry records

Before interpreting depth differences, the experiment record must establish or explicitly mark `UNKNOWN` for:

- Parallelism between the two target planes.
- Angle between the camera optical axis and the target-plane normal.
- Spatial location and boundaries of both ROIs, including exclusion of edges, mixed pixels, holes, and occluding boundaries.
- Depth coordinate system and units. For this protocol, raw D435 Z16 samples are camera optical-axis depth coordinates after application of the verified device depth scale; they are not Euclidean range unless separately transformed.
- Physical definition and measurement direction of the step height.
- Camera-to-target distance definition and the reference point from which it is measured.

### Approximately fronto-parallel configurations

Only when the two planes are sufficiently parallel and the target normal is sufficiently aligned with the camera optical axis according to pre-reviewed geometric tolerances may the difference between robust plane-ROI depth estimates be used as an approximation to step height. The ROI estimator and the alignment tolerances must be declared before result interpretation.

### Inclined configurations

For an inclined target or camera, `abs(Z2-Z1)` must not be assumed to equal physical step height. A reviewed 3D geometric relationship using documented camera intrinsics, coordinate frames, plane geometry, and target pose is required. Until that relationship is reviewed, the geometric comparison is `UNVERIFIED`.

The D435 depth data under test must not be used by itself to construct a plane and then label that plane as independent ground truth. D435-only fitting may be used for diagnostics, but never as the independent reference chain.

## Depth validity and valid-but-wrong classification

- Raw-depth validity prerequisite: the decoded raw depth sample must be a finite positive value after applying the verified depth scale. Zero, missing, non-finite, out-of-range, or otherwise invalid samples do not satisfy this prerequisite.
- A positive value is only syntactically valid; validity alone does not establish geometric correctness.
- `REFERENCE_U95 = UNVERIFIED` until the physical reference uncertainty budget is reviewed and supported.
- `VALID_BUT_WRONG_GT = UNVERIFIED` until the independent reference, geometry correction, and decision threshold are approved.
- A future valid-but-geometrically-wrong decision may only be made when the raw-depth validity prerequisite is satisfied and the reviewed geometric error criterion is exceeded relative to the independent reference and its approved uncertainty. STEP1 assigns no fabricated numerical threshold.

## Uncertainty budget template

| Contribution | Evidence/source | Estimate | Distribution/model | Standard uncertainty | Status |
|---|---|---:|---|---:|---|
| Caliper measurement repeatability | Repeated repositioned measurements |  |  |  | `UNKNOWN` |
| Caliper accuracy or calibration | Datasheet/certificate/verification |  |  |  | `UNKNOWN` |
| Step-surface flatness | Physical inspection/metrology |  |  |  | `UNKNOWN` |
| Step-plane parallelism | Physical inspection/metrology |  |  |  | `UNKNOWN` |
| Target installation error | Setup measurement |  |  |  | `UNKNOWN` |
| Camera pose error | Alignment/pose measurement |  |  |  | `UNKNOWN` |
| Depth quantization | Verified depth scale and encoding |  |  |  | `UNKNOWN` |
| ROI localization | ROI definition and sensitivity study |  |  |  | `UNKNOWN` |
| Environmental variation | Temperature, illumination, vibration, time |  |  |  | `UNKNOWN` |

No combined uncertainty or `U95` may be reported until the components, assumptions, correlations, coverage factor, and calculation have been reviewed.

## Data-state vocabulary

- `PLANNED`: protocol entry exists; no measurement or capture is claimed.
- `MEASURED`: independent physical reference measurement completed and documented.
- `CAPTURED`: camera data captured and file integrity verified.
- `INVALID`: attempted record rejected with a documented reason; never silently replaced.
- `NOT_CAPTURED`: planned or attempted entry for which no valid capture exists.

## Stage restrictions

During STEP1:

- Do not start ROS, a ROS launch file, a camera node, or a RealSense stream.
- Do not enable, disable, command, or move the robot, arm, wrist, or gripper.
- Do not connect to or command CAN hardware.
- Do not modify firmware, EEPROM, camera parameters, or system configuration.
- Do not acquire experimental data.
- Do not train or run inference.
- Do not enter Stage05.

## Review and sign-off

This reconstructed protocol remains a draft. It may become formally frozen only after explicit user review and approval. STEP1 completion alone must not change the status to `FROZEN`.
