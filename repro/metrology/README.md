# Reference metrology record

This folder documents the caliper reference used in the manuscript
*Reference-Graded Characterisation of an Active-Stereo Depth Sensor*.

## Values used in the paper

`reference_values.csv` lists the five reference values used in Table 3 of the
main text. They are the means of four caliper readings of the total height minus
four readings of the base thickness (for S00, four readings of the plate
thickness). The standard deviation over the four readings is 0.02 mm.

## Provenance

The readings were recorded on paper and transcribed. The paper sheets are
retained by the authors; the machine-readable transcription is
`reference_readings_template.csv`. The original sheets are available from the
authors on request. If a scan or a full transcription becomes available, deposit
it in this folder; do not reconstruct readings from the summary values.

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

- [x] Five reference values transcribed (Table 3)
- [ ] Raw paper sheet scanned or fully transcribed
- [ ] Instrument model / calibration status recorded
- [ ] Template filled and checked against the paper sheet

**Deposit mode (2026-11-18):** summary values + blank template. The raw paper
sheet is not digitised; the manuscript therefore states that the original sheets
are available from the authors on request. If a scan or full transcription
becomes available, replace the blank template with it and update this status.
