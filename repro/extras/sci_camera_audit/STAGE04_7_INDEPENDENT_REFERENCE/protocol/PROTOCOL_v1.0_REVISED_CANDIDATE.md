# STAGE04.7 Independent Physical Reference Measurement Protocol — Revised Candidate

## Document control

- Protocol lineage: revision candidate derived from `PROTOCOL_FREEZE_v1.0.md`
- Source protocol SHA256: `2c154df8309ec42db314b9aa3a0476d5e1cdf346877ec91961c4df38ae2dfd24`
- Candidate version: `1.0-revised-candidate`
- Candidate status: `REVISED_CANDIDATE_PENDING_USER_SIGNOFF`
- Formal freeze status: `NOT_FROZEN`
- Historical claim: none; this candidate was created during STEP2A.
- Change rule: no experimental parameter may be adjusted in response to later results. Any further pre-freeze change requires documented user review.

The source draft remains preserved and is not superseded until the user explicitly approves and freezes a reviewed protocol.

## Scientific objective and endpoint boundary

The independent physical reference chain uses a caliper or another reviewed physical instrument to assess whether positive, syntactically valid Intel RealSense D435 depth observations exhibit a geometrically significant discrepancy.

The first scientific endpoint in this stage is:

`STEP_GEOMETRY_DISCREPANCY`

This endpoint must not automatically be labelled:

`PER_PIXEL_VALID_BUT_WRONG_GT`

A step-geometry discrepancy is an aggregate geometric finding. It becomes evidence relevant to valid-but-geometrically-wrong depth only after the reference uncertainty is adequate, the camera/target geometry is sufficiently constrained, raw-depth validity is established, and a reviewed decision rule is applied. It does not by itself establish per-pixel ground truth.

## Fixed candidate experiment parameters

| Parameter | Value |
|---|---|
| CAMERA | `RIGHT_D435` |
| CAMERA_SERIAL | `317422072133` |
| DEPTH_PROFILE_REQUESTED | `848x480 Z16 30FPS` |
| COLOR_PROFILE_PRECHECK_REQUESTED | `640x480 RGB8 30FPS` |
| DEPTH_POSTPROCESSING | `OFF` |
| DISTANCES_MM | `400,600,800` |
| POSITIONS | `CENTER,LEFT,RIGHT` |
| STEP_TARGETS | `S20,S40,S60` |
| INDEPENDENT_REPLACEMENTS_PER_CONFIGURATION | `5` |
| FRAMES_PER_REPLACEMENT | `30` |
| TOTAL_CONDITIONS | `27` |
| TOTAL_SETUP_REPEATS | `135` |
| TOTAL_FRAMES_PLANNED | `4050` |
| FIRST_PILOT | `S40_600MM_CENTER` |
| FIRST_PILOT_REPEATS | `5` |

Arithmetic:

- `3 step targets x 3 distances x 3 positions = 27 configurations`
- `27 configurations x 5 independent replacements = 135 experimental units`
- `135 experimental units x 30 within-unit temporal frames = 4050 planned frames`

SDK enumeration has shown the requested depth and color profiles separately in the device's advertised profile lists. This does not prove that both requested streams have completed simultaneous acquisition. Simultaneous streaming remains unverified until a separately authorized precheck is completed.

## Experimental measurands

### Independent physical reference

`h_ref` is the actual step height obtained from the independent physical reference measurement, primarily the reviewed caliper procedure. The target label (`S20`, `S40`, or `S60`) is not a measurement and must never be substituted for `h_ref`.

### Camera-derived estimate

`h_D435` is the step height estimated from raw D435 depth data using a predeclared, geometrically valid reconstruction method and documented ROIs. Raw Z16 values must first use the verified current device depth scale.

### Comparison error

`e_h = h_D435 - h_ref`

The sign convention must be retained. An absolute error may be reported additionally, but must not replace the signed comparison error in the primary record.

## Independent reference measurement procedure

For each target (`S20`, `S40`, `S60`):

1. Use at least five identified physical positions (`P1` through `P5` in the initial sheet).
2. Remove and reposition the caliper before each measurement.
3. Make three independently repositioned readings per position.
4. A human operator must enter the actual measured millimetres, operator, instrument model, instrument resolution, calibration status, and measurement time.
5. Do not pre-populate, generate, or infer actual dimensions from the target ID or a nominal label.
6. Caliper display resolution is not accuracy, calibration uncertainty, standard uncertainty, or `U95`.
7. Unsupported instrument properties remain `UNKNOWN`.

The independent reference must not be derived from the same D435 depth observations being tested.

## Geometry definition and conditions

### Physical step height

The true physical step height is the perpendicular separation between representative surfaces of the two step planes under the reviewed target definition. Its direction is tied to the target surface normal, not automatically to the camera optical axis.

### Required geometric records

Every interpreted configuration must record or explicitly mark `UNKNOWN` for:

- The normal vector or orientation of the step surfaces.
- Parallelism of the two measured surfaces and the method used to assess it.
- The exact definition and direction of true step height.
- The D435 depth coordinate system, depth units, and verified depth scale.
- The spatial location, size, shape, and selection rule for both ROIs.
- Exclusion rules for edges, mixed pixels, holes, occlusions, and invalid samples.
- Relative pose between the camera and the step target, including the optical-axis/target-normal angle.
- The reference point and direction used for camera-to-target distance.

Raw D435 Z16 depth represents camera optical-axis depth after application of the verified current depth scale; it is not automatically Euclidean range or perpendicular target-plane separation.

### Permitted and prohibited comparisons

For a predeclared approximately fronto-parallel configuration meeting reviewed angular and parallelism tolerances, a difference between robust plane-ROI depth estimates may be used as an approximation to step height, with the approximation and its uncertainty explicitly included.

The median depth of two ROIs at different spatial locations must not be subtracted and unconditionally equated to true step height. For inclined or otherwise nonconforming geometry, `abs(Z2-Z1)` is not a valid general rule. A reviewed 3D relationship using documented camera intrinsics, coordinate frames, target pose, and plane geometry is required.

Raw depth may be used to estimate the camera-derived measurand `h_D435`. That same estimate, plane, or reconstruction must not be relabelled as independent reference truth.

## Depth validity

A raw depth sample passes the syntactic validity prerequisite only if its decoded value is finite and strictly positive after applying the verified current depth scale. Zero, missing, non-finite, saturated when defined as invalid, or out-of-scope samples do not pass. Syntactic validity alone does not establish geometric correctness.

## Uncertainty framework

The following uncertainty layers are distinct and must be estimated and reported separately before any combined decision:

### `u_reference`

Reference-measurement standard uncertainty. Candidate contributions include caliper repositioning repeatability, instrument accuracy or calibration evidence, surface flatness, surface parallelism, fixture effects, contact method, operator effects, and environmental variation.

### `u_depth_repeatability`

D435 observation repeatability under one configuration and across independently replaced configurations. Within-repeat temporal variation and between-replacement variation must not be conflated. Depth quantization may be recorded as a separate component where justified.

### `u_geometry`

Uncertainty arising from camera/target pose, ROI localization, plane estimation, intrinsics, extrinsics, target geometry, coordinate transformation, and any approximation used to derive `h_D435`.

### `u_comparison`

Standard uncertainty associated with `e_h = h_D435 - h_ref`. Under documented reasonable independence assumptions, variance components may be combined. If material correlations exist or cannot be neglected, covariance terms must be included. A mechanical root-sum-of-squares calculation is prohibited when its independence assumptions are unsupported.

Any expanded uncertainty must identify the standard uncertainty, coverage factor, coverage assumptions, and included covariance terms. No numerical `U95` may be fabricated. Caliper display resolution must not be used as instrument accuracy or as `U95`.

Current research gates:

- `REFERENCE_U95 = UNVERIFIED`
- `VALID_BUT_WRONG_GT = UNVERIFIED`

These values must remain unchanged until real reference data, geometry review, and uncertainty analysis are complete and approved.

## Statistical unit and dependence structure

Each configuration has five independently re-established physical placements. Each physical placement is one experimental unit.

The 30 frames collected during one placement form a within-placement time series of repeated observations. They are not 30 independent physical experiments. Temporal dependence, autocorrelation, and within-placement aggregation must be considered.

Primary inferential statistics must use the actual placement-level experimental unit or an explicitly reviewed hierarchical/repeated-measures model. The planned 4050 frames must not be treated directly as 4050 independent samples, and frame-level pseudoreplication is prohibited.

## Data-state vocabulary

- `PLANNED`: protocol record exists; no measurement or capture is claimed.
- `MEASURED`: independent reference measurement completed and documented.
- `CAPTURED`: camera data captured and file integrity verified.
- `INVALID`: attempted record rejected with a documented reason.
- `NOT_CAPTURED`: no valid capture exists for that planned or attempted record.

## Safety and execution gates

- Physical robot stability and wrist-camera mounting must be confirmed by authorized personnel using `hardware/PHYSICAL_SAFETY_CONFIRMATION.md` before camera streaming.
- Process inspection cannot substitute for physical safety confirmation.
- Robot movement, robot enable/disable commands, CAN commands, gripper actions, and ROS robot launch files are prohibited.
- Camera viewpoint must not be adjusted through robot joint movement.
- No firmware, EEPROM, emitter, exposure, or persistent camera setting may be modified.
- No alignment, spatial filtering, temporal filtering, hole filling, or depth completion may be used for the raw-depth primary stream.
- Formal 135-unit collection requires a separate authorization after the short SDK precheck.
- Stage05, training, and inference remain outside this stage.

## Candidate review and sign-off

This document resolves the two STEP2 scientific-review gaps in a new candidate while preserving the original draft. It is not formally frozen. Only explicit user review and sign-off may authorize creation of a final frozen protocol and its integrity record.
