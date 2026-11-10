# S40 Independent Physical Measurement Guide

## Scope and status

- Target ID: `S40`
- Nominal step height: `40 mm`
- Actual step height: `NOT_MEASURED`
- Document role: on-site preparation and measurement guide
- Formal experiment authorization: `NO`

The `S40` label and nominal 40 mm value are identifiers and design intent only. They must not be entered as the actual height. The actual value `h_ref` must come from documented physical measurements.

## Required target construction

Use a rigid, opaque, matte, two-plane step target. Both reference planes must be mechanically stable and large enough to support physical measurement and later depth ROIs away from the step edge. Glossy, transparent, translucent, flexible, moving, or poorly fixed surfaces are unsuitable unless separately reviewed.

Before measurement, inspect and record:

- Whether both plane surfaces appear intact, clean, rigid, and matte.
- How the two planes are fixed relative to one another.
- Whether both planes are intended to be parallel.
- Any visible warping, coating thickness, burrs, edge damage, recesses, or compliant layers.
- Whether the target can remain fixed without robot motion.

An appearance check is not a numerical flatness or parallelism measurement. Unsupported properties remain `UNKNOWN`.

## Definition of the physical measurand

`h_ref` is the perpendicular distance between the two defined reference planes. The measurement direction is the common surface-normal direction when the planes are sufficiently parallel.

Before using a caliper, identify and document:

1. Reference plane A and reference plane B.
2. The exact contact surfaces used by the caliper.
3. The normal direction along which separation is measured.
4. Whether the contact geometry measures the two reference planes themselves or an intermediate/support feature.
5. The mapping of physical positions `P1` through `P5` on the target.

The caliper reading is admissible as `h_ref` only when the measured quantity corresponds to the normal separation of the two declared reference planes. If the correct reference surfaces cannot be contacted, their parallelism cannot be reasonably established, or the caliper geometry measures another feature, stop and report the limitation.

Do not automatically substitute support-block thickness, spacer thickness, nominal CAD dimensions, target labels, or an inaccessible backing feature for the physical step height.

## Instrument record

Record before entering any measured value:

- Instrument ID.
- Caliper manufacturer and model.
- Serial number, if present.
- Display resolution.
- Accuracy specification source, if available.
- Calibration or verification status and date, if available.
- Zero-check result and any observed damage or contamination.
- Operator name or approved identifier.
- Measurement date, time, and timezone.

Display resolution is not accuracy and is not `U95`. Missing evidence must be recorded as `UNKNOWN`; it must not be inferred.

## Measurement-position plan

Use five distinct and reproducible positions, `P1` through `P5`, distributed over the usable step interface so that local variation can be observed. Mark or describe each position without damaging the reference surfaces. Do not place a contact point on a burr, chamfer, rounded edge, loose coating, or visibly damaged region.

For each position:

1. Clean and visually inspect the contact region using the approved laboratory procedure.
2. Check instrument zero according to the instrument procedure.
3. Place the caliper on the declared reference surfaces without tilting or excessive force.
4. Allow the reading to stabilize.
5. Enter the displayed value in `S40_MEASUREMENT_ENTRY.csv`.
6. Remove the caliper completely and independently reposition it before the next repeat.
7. Perform exactly three recorded repositioned measurements unless a deviation is documented.

This produces 5 positions × 3 repositioned readings = 15 planned measurement records. Do not average values during entry and do not overwrite an anomalous reading. Record the observation and explain any invalidation separately.

## Geometry and quality hold points

Stop and report rather than declaring `h_ref` if any of the following applies:

- The two reference planes cannot be unambiguously identified.
- The caliper cannot contact the correct reference surfaces.
- The measurement direction is not the plane-normal direction.
- The planes or target move under measurement force.
- Parallelism, flatness, or mounting is visibly questionable and cannot be evaluated.
- Different positions measure different physical features.
- Instrument model, resolution, zero condition, or calibration status cannot be recorded.

Unknown flatness, parallelism, fixture effects, and instrument accuracy remain uncertainty-budget inputs. No `REFERENCE_U95` may be generated from the 15 readings alone without the reviewed uncertainty model.

## Relationship to D435 measurements

The D435-derived quantity is `h_D435`; the independent physical quantity is `h_ref`; their signed comparison is `e_h = h_D435 - h_ref`. The same D435 raw-depth estimate must never be reused as independent reference truth.

This guide does not authorize camera capture, robot motion, ROS startup, formal S40 acquisition, or protocol freezing.
