# S40 Independent Physical Reference Target Setup Guide

## Scope and current state

- Target: `S40`
- Nominal plane separation: `40 mm`
- Physical target built: `UNVERIFIED`
- Actual reference height: `NOT_MEASURED`
- Camera stream authorized by this guide: `NO`
- Formal experiment authorized by this guide: `NO`

The nominal 40 mm value is a design requirement and target label. It is not an observed reference value and must not be entered as `h_ref`.

## 1. Target design requirements

The S40 target must contain two rigid, opaque, matte reference planes:

1. A smaller front plane located in front of a larger rear plane when viewed from the D435.
2. The two useful reference surfaces should be as parallel as practicable.
3. Their nominal separation should be 40 mm along the intended camera optical-axis direction in the approximately fronto-parallel setup.
4. Both planes must be simultaneously visible inside the D435 Depth field of view, with usable interior areas away from the step edge.
5. The target must be fixed independently using a stable fixture or support and must not rely on the robot arm or gripper for holding.
6. The structure must permit a suitable caliper method to contact or otherwise measure the declared reference planes along their normal direction.
7. The fixture, spacer, coating, adhesive, and support must not obscure which surfaces define the physical measurand.

Do not use transparent, translucent, glossy, flexible, loose, visibly warped, or unstable surfaces without a separately reviewed justification.

## 2. Definition of the reference height

Let plane A be the smaller front reference surface and plane B be the larger rear reference surface. The physical reference height `h_ref` is the perpendicular normal separation between the representative surfaces of A and B.

Before measurement, record:

- The physical identity and boundary of plane A.
- The physical identity and boundary of plane B.
- The target normal direction.
- The contact points or contact regions used by the caliper.
- The five measurement positions `P1` through `P5`.
- How the fixture prevents motion or deformation during measurement.

The nominal thickness of a spacer or support block must not be substituted for actual step height. A spacer may differ from the final reference-plane separation because of coating, adhesive, seating, deformation, burrs, nonparallel surfaces, or assembly tolerances.

If the caliper cannot contact the correct reference surfaces, if the measurement direction is not the declared normal direction, or if plane parallelism cannot be reasonably assessed, record the limitation and stop. Do not manufacture a value from nominal dimensions.

## 3. Alignment relative to the camera

The intended pilot places the target approximately fronto-parallel so that the target normal is approximately aligned with the camera optical axis. This condition must be checked and recorded; it must not be assumed from visual appearance alone.

If the reference planes are visibly or measurably tilted relative to the camera, the difference between two Depth-ROI Z estimates is not automatically equal to `h_ref`. In an inclined configuration, the comparison requires a reviewed three-dimensional geometric relationship using camera coordinates, intrinsics, target pose, plane normals, and ROI locations.

Two ROIs at different image positions may have different Z solely because of plane tilt. Therefore a raw median difference such as `abs(Z_B - Z_A)` must not be used unconditionally as physical normal separation.

## 4. Fixture and visibility preparation

- Fix the target on a rigid support independent of the robot.
- Confirm the fixture does not bend either reference plane.
- Confirm the target cannot rock, slide, or rotate during measurement.
- Route cables and place the target without creating collision or snag hazards.
- Position the smaller front plane so it does not fully occlude the rear plane.
- Ensure both planes have sufficiently large Depth-image interior regions for ROIs away from the step boundary.
- Do not move the robot to improve the viewpoint.
- Record nominal and actual camera-to-target distance using declared physical reference points.

Physical construction, fixture stability, plane visibility, and safety must be confirmed on site. Software process state cannot establish these facts.

## 5. Caliper and operator record

Before entering any height value, record:

- Caliper/instrument identity, manufacturer, model, and serial if available.
- Display resolution.
- Manufacturer accuracy specification or calibration evidence, if available.
- Calibration/verification status and date.
- Zero-check status.
- Operator identity.
- Measurement timestamp and timezone.
- Temperature and relevant environmental conditions.

Instrument resolution is not accuracy and must not be used as `U95`.

Measure each of `P1` through `P5` three times. Remove and independently reposition the caliper before every repeat. Enter the 15 unaggregated readings in `S40_MEASUREMENT_ENTRY.csv`; do not prefill, silently replace, or average readings during entry.

## 6. Depth ROI preparation for the later pilot

Primary ROIs must be defined in the raw Depth image coordinate system. RGB pixel locations must not be copied directly to Depth coordinates without a reviewed projection using the appropriate intrinsics and depth-to-color extrinsics.

For each reference plane, select an interior ROI that avoids:

- The physical step edge.
- Occlusion boundaries and mixed pixels.
- Zero-depth holes.
- Saturated values.
- Damaged, curved, glossy, shadowed, or nonrepresentative areas.

Record ROI coordinates, positive-valid ratio, zero fraction, saturation count, and the physical surface represented. A positive depth value is not evidence of geometric correctness.

## 7. Stop conditions

Stop setup or measurement and report `UNVERIFIED` if:

- The target has not been physically built or inspected.
- Either reference plane is ambiguous, unstable, nonrigid, or inaccessible.
- Both planes cannot be seen simultaneously in the Depth field of view.
- Correct caliper contact or normal-direction measurement is impossible.
- Plane parallelism, flatness, or fixture deformation is questionable and undocumented.
- Robot movement would be required.
- A fresh physical safety confirmation has not been completed for the later experiment.

This guide prepares a reference method only. It does not establish `REFERENCE_U95`, per-pixel ground truth, or a valid-but-geometrically-wrong conclusion.
