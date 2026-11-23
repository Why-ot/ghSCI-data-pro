# Reference metrology record

This folder documents the caliper reference used in the manuscript
*Error Endpoints Decide Whether Depth-Reliability Scores Work: Evidence from a Reference-Graded Active-Stereo Sensor*.

## Values used in the paper

`reference_values.csv` lists the five reference values used in Table 3 of the
main text. They are the means of four caliper readings of the total height minus
four readings of the base thickness (for S00, four readings of the plate
thickness). The standard deviation over the four readings is 0.02 mm.

## Provenance

The readings were recorded on paper and are transcribed in
`reference_readings.csv`, one row per target, orientation, measurand and position.
`derive_reference.py` reproduces the five values in `reference_values.csv` from
them; run it in this folder.

Granularity differs between targets, and the file says so in its `reading_type`
column:

* S20, S40-B and S60 - eight individual readings each (four of the base
  thickness, four of the total height).
* S40-A - the mean of each orientation's four readings, not the four readings.
  The reference step is the mean of the two orientation means, so the coefficient
  reproduces; the 0.02 mm standard deviation for S40-A is **not** recomputable
  from this file and is carried over from the paper sheet.
* S00 - a single reported plate thickness.

Do not reconstruct a missing reading from a mean.

An earlier partially digitised reduction (`reference_steps.csv` and
`reference_repeatability.csv`, from the 21 mm-base trial batch) is superseded
and is not used. The public repository README (`repro/analysis/out/README.md`)
records why those files were removed.

## Template

`reference_readings_template.csv` has one row per target, orientation, measurand
and position: four positions per measurand, four readings per position. Fill
`reading_mm`; record the instrument, calibration status, operator and date. The
four readings are those used to compute the 0.02 mm standard deviation; do not
infer a missing reading from the mean.

## Status

- [x] Five reference values reproduced from the deposited readings
- [x] Readings for S20, S40-B, S60 and S00 transcribed individually
- [x] S40-A recorded as four-reading means per orientation
- [ ] S40-A individual readings (not in the retained record)
- [ ] Instrument model / calibration status recorded
- [ ] Paper sheet scanned

**Deposit mode (2026-11-19):** readings deposited and reduced by
`derive_reference.py`. S40-A is at orientation-mean granularity, as stated in the
file and in Supplementary Section S5.
