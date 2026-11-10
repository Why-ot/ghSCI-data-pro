# STEP2 Protocol Scientific Review

- Review time: `2026-10-26T11:53:34+08:00`
- Reviewed file: `protocol/PROTOCOL_FREEZE_v1.0.md`
- Reviewed protocol SHA256: `2c154df8309ec42db314b9aa3a0476d5e1cdf346877ec91961c4df38ae2dfd24`
- Protocol status observed: `DRAFT_RECONSTRUCTED_PENDING_USER_SIGNOFF`
- Review result: `ISSUES_FOUND`
- Protocol modified during STEP2: `NO`

## Constraint review

| ID | Required scientific constraint | Result | Protocol evidence or issue |
|---|---|---|---|
| PR-01 | Physical step height versus camera Z-depth geometry is explicit | PASS | The primary measurand is defined as perpendicular plane separation; Z16 is identified as camera optical-axis depth; `abs(Z2-Z1)` is prohibited as a general arbitrary-pose step-height rule; inclined configurations require reviewed 3D correction. |
| PR-02 | Reference uncertainty, depth repeatability, and combined comparison uncertainty are distinguished | ISSUE | The protocol includes a reference uncertainty budget and prohibits unsupported combined uncertainty, but it does not explicitly define depth-measurement repeatability as a separate quantity or clearly distinguish all three uncertainty layers. |
| PR-03 | No valid-but-wrong GT approval before U95 verification | PASS | `REFERENCE_U95 = UNVERIFIED` and `VALID_BUT_WRONG_GT = UNVERIFIED`; no numerical threshold is fabricated. |
| PR-04 | Thirty frames are repeated observations within one capture repeat, not 30 independent experimental units | ISSUE | `FRAMES_PER_REPEAT = 30` and the arithmetic are recorded, but the required independence statement is absent. |
| PR-05 | Actual target dimensions must be manually entered and not generated | PASS | The protocol forbids pre-populating or inferring measured dimensions; the measurement sheet leaves all actual measurements empty. |
| PR-06 | `848x480 Z16 30FPS` is requested and not yet verified | PASS | The profile is named `DEPTH_PROFILE_REQUESTED`, and the protocol explicitly requires later SDK verification before a pilot. |

## PROTOCOL_REVIEW_ISSUES

1. `PRI-001`: Explicitly separate and define independent reference-measurement uncertainty, depth-measurement repeatability, and combined comparison uncertainty.
2. `PRI-002`: Explicitly state that the 30 frames within a repeat are repeated observations of one experimental unit and are not 30 independent experimental units.

These are review findings only. STEP2 did not edit the protocol and did not change its status to `FROZEN`.

## Capture gate consequence

The task requires all preceding gates to pass before the single 20-second stream test. Because `PRI-001` and `PRI-002` remain unresolved, the stream gate is `FAILED_GATE` and SDK capture is `NOT_STARTED`.
