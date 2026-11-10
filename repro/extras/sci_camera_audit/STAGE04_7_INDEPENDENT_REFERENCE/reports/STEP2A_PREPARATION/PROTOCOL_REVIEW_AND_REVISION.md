# STEP2A Protocol Review and Revision Report

## Original protocol integrity gate

- Expected SHA256: `2c154df8309ec42db314b9aa3a0476d5e1cdf346877ec91961c4df38ae2dfd24`
- Observed SHA256 before revision work: `2c154df8309ec42db314b9aa3a0476d5e1cdf346877ec91961c4df38ae2dfd24`
- Observed SHA256 after preparation work: `2c154df8309ec42db314b9aa3a0476d5e1cdf346877ec91961c4df38ae2dfd24`
- Integrity gate: `PASS`
- Original file modified: `NO`

The original draft remains at `protocol/PROTOCOL_FREEZE_v1.0.md`. It was neither overwritten nor relabelled as frozen.

## Revised candidate

- File: `protocol/PROTOCOL_v1.0_REVISED_CANDIDATE.md`
- Status: `REVISED_CANDIDATE_PENDING_USER_SIGNOFF`
- Formal freeze status: `NOT_FROZEN`
- SHA256: `eefc0d3b195ca3892559d03d25711b5163a72849bebb04ff95d8b9fa1f22f9cd`

## Resolution of STEP2 scientific gaps

### Gap 1: uncertainty layers

Status: `RESOLVED_IN_REVISED_CANDIDATE`

The candidate separately defines:

- `u_reference`: uncertainty from the independent reference chain.
- `u_depth_repeatability`: D435 within-placement and between-placement repeatability.
- `u_geometry`: pose, ROI, calibration, reconstruction, and approximation uncertainty.
- `u_comparison`: uncertainty associated with `e_h = h_D435 - h_ref`.

It permits variance combination only under documented reasonable independence assumptions and requires covariance terms when correlations are material. It prohibits fabricated `U95` values and prohibits treating caliper display resolution as accuracy or expanded uncertainty.

### Gap 2: experimental unit

Status: `RESOLVED_IN_REVISED_CANDIDATE`

The candidate states that each of five independently re-established placements is an experimental unit. The 30 frames within one placement are a time series of repeated observations, not 30 independent physical experiments. It explicitly prohibits treating 4050 frames as 4050 independent samples.

## Other scientific clarifications

- `h_ref`: independently measured physical step height.
- `h_D435`: raw-depth-derived step-height estimate under reviewed geometry.
- `e_h = h_D435 - h_ref`.
- ROI median differences cannot be unconditionally equated with true step height.
- D435-derived geometry cannot be reused as independent reference truth.
- `STEP_GEOMETRY_DISCREPANCY` is the initial endpoint and is not automatically `PER_PIXEL_VALID_BUT_WRONG_GT`.
- `REFERENCE_U95 = UNVERIFIED` remains unchanged.
- `VALID_BUT_WRONG_GT = UNVERIFIED` remains unchanged.
- Individual support for requested depth and color profiles is not represented as proof of simultaneous streaming.

## Review conclusion

`PROTOCOL_SCIENTIFIC_GAPS_RESOLVED = YES` applies to the new revised candidate only. The candidate still requires explicit user review and sign-off. No final frozen protocol was created.
