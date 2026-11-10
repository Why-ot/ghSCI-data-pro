# STAGE04.7 STEP1 Protocol Materialization Report

## Outcome

| Field | Result |
|---|---|
| PROTOCOL_FILE_CREATED | `YES` |
| PROTOCOL_STATUS | `DRAFT_RECONSTRUCTED_PENDING_USER_SIGNOFF` |
| EXPERIMENT_MANIFEST_ROWS | `135` |
| PLANNED_TOTAL_FRAMES | `4050` |
| RIGHT_D435_SERIAL | `317422072133` |
| REAL_CAPTURE_STARTED | `NO` |
| ROBOT_MOVEMENT | `NO` |
| READY_FOR_PROTOCOL_REVIEW | `YES` |
| NEXT_TASK | `STAGE04_7_STEP2_RIGHT_D435_SDK_PRECHECK` |

This STEP1 created a new reviewable protocol from the user-approved design parameters. It does not claim that the protocol file existed historically, and it does not assign a historical freeze date or frozen hash.

## Created directory structure

```text
STAGE04_7_INDEPENDENT_REFERENCE/
├── CAMERA_PROFILE_REQUIREMENTS.json
├── EQUIPMENT_REGISTER.csv
├── EXPERIMENT_MANIFEST.csv
├── PILOT_CAPTURE_PLAN.csv
├── REFERENCE_MEASUREMENT_SHEET.csv
├── hardware/
│   └── STATIC_EXPERIMENT_SAFETY.md
├── protocol/
│   └── PROTOCOL_FREEZE_v1.0.md
├── raw_capture/
├── reference_measurements/
├── reports/
│   ├── FILE_SHA256SUMS.txt
│   └── STAGE04_7_STEP1_REPORT.md
├── results/
└── scripts/
    └── validate_stage04_7.py
```

The empty `raw_capture`, `reference_measurements`, and `results` directories are intentional. No experimental data was created.

## Materialized protocol parameters

- Camera: `RIGHT_D435`
- Serial: `317422072133`
- Requested raw depth profile: `848x480 Z16 30FPS`
- Depth postprocessing: `OFF`
- Step targets: `S20,S40,S60`
- Distances: `400,600,800 mm`
- Positions: `CENTER,LEFT,RIGHT`
- Repeats per condition: `5`
- Frames per repeat: `30`
- Conditions: `27`
- Setup repeats: `135`
- Planned frames: `4050`
- First pilot: `S40_600MM_CENTER`
- First-pilot repeats: `5`

## CSV and JSON checks

| Artifact | Parsed data rows | Result |
|---|---:|---|
| `EQUIPMENT_REGISTER.csv` | 6 | PASS |
| `REFERENCE_MEASUREMENT_SHEET.csv` | 45 | PASS; all `measured_mm` fields empty |
| `EXPERIMENT_MANIFEST.csv` | 135 | PASS; all IDs unique and all records `PLANNED` |
| `PILOT_CAPTURE_PLAN.csv` | 5 | PASS; all records `PLANNED` |
| `CAMERA_PROFILE_REQUIREMENTS.json` | N/A | PASS; valid JSON and requested profile consistent |

Validated arithmetic:

- `3 x 3 x 3 x 5 = 135` experiment records.
- `135 x 30 = 4050` planned frames.
- No `actual_frames` value was populated.
- No record was marked `MEASURED`, `CAPTURED`, or `INVALID`.

The read-only validator reported `VALIDATION_STATUS=PASS`, `UNIQUE_EXPERIMENT_IDS=PASS`, `JSON_PARSE=PASS`, and `DIRECTORY_STRUCTURE=PASS`.

## SHA256 before report creation

| File | SHA256 |
|---|---|
| `CAMERA_PROFILE_REQUIREMENTS.json` | `05350b288439a50f7b674b2e3718deb700dee02ae6df69dfdefcf090efde4d49` |
| `EQUIPMENT_REGISTER.csv` | `a5b744becbb81086fb05a990e28503cf7358ebda712459fa0215d9b9f502c450` |
| `EXPERIMENT_MANIFEST.csv` | `3da2ce81b879b61a35db7ff3ff5552c3196c828205204a3db6695a665e31059b` |
| `PILOT_CAPTURE_PLAN.csv` | `8b19a30138993dd997807e0d6812e882dea6209a24de7dc3c4ae9572be1ffbfc` |
| `REFERENCE_MEASUREMENT_SHEET.csv` | `92a17a08c2479dfe52c7607dc45ae9da814688151ebf0f5a022a658e922159d3` |
| `hardware/STATIC_EXPERIMENT_SAFETY.md` | `84e2bbdb3d1dccee3d398d5c0a9b448eb205239302a40e1c2cd83a0f9269e067` |
| `protocol/PROTOCOL_FREEZE_v1.0.md` | `2c154df8309ec42db314b9aa3a0476d5e1cdf346877ec91961c4df38ae2dfd24` |
| `scripts/validate_stage04_7.py` | `ca3815ecc1e95bc6e95da081cc6968b1b6a168bfa561cc9a82cc6be37c8fb99d` |

The companion `reports/FILE_SHA256SUMS.txt` is generated after this report so that it can include the report's own SHA256. The checksum ledger does not hash itself.

## Physical conditions still unverified

- Caliper manufacturer/model, serial number, display resolution, accuracy, and calibration status.
- Actual dimensions of `S20`, `S40`, and `S60`.
- Caliper repeatability based on repositioned measurements.
- Step-surface flatness and plane parallelism.
- Target mounting error and stability.
- Camera optical-axis to target-normal angle and its uncertainty.
- Exact ROI definitions and ROI localization sensitivity.
- Verified D435 depth scale and coordinate conventions for the requested profile.
- Environmental variation during physical measurement and capture.
- Reviewed 3D correction for inclined configurations.
- Combined reference uncertainty and `REFERENCE_U95`.
- Numerical ground-truth decision rule for `VALID_BUT_WRONG_GT`.
- Static physical safety of any wrist-mounted camera arrangement.

Accordingly, `REFERENCE_U95 = UNVERIFIED` and `VALID_BUT_WRONG_GT = UNVERIFIED`.

## Conditions for the next task

1. The user must review this reconstructed protocol and either approve it for formal freezing or identify corrections.
2. STEP1 must not itself change the protocol status to `FROZEN`.
3. Before capture, the right D435 serial and exact `848x480 Z16 30FPS` profile must be verified through the separately authorized SDK precheck.
4. The SDK precheck must remain static and must not start ROS or robot control.
5. Physical reference instrumentation and geometry fields may remain `UNKNOWN` during protocol review, but must be resolved or explicitly dispositioned before a valid ground-truth claim.
6. No acquisition may be interpreted as valid-but-geometrically-wrong ground truth until the independent reference chain and uncertainty rule are approved.

After user review, the named next task is `STAGE04_7_STEP2_RIGHT_D435_SDK_PRECHECK`. This report does not execute or authorize that task.

## Safety and scope declaration

- ROS started: `NO`
- Camera stream started: `NO`
- Experimental data captured: `NO`
- Robot control started: `NO`
- Robot/CAN command sent: `NO`
- Robot movement: `NO`
- Software installation or upgrade: `NO`
- Firmware/EEPROM modification: `NO`
- Stage05 entered: `NO`
