# Reproduction material

This folder holds everything needed to regenerate the numbers in the paper apart
from the raw sensor captures, which live in `../parts/` as split archives.

```
repro/
  evidence/CSV/SCI_RESTART_20261008/   frozen per-scene and per-candidate tables
  analysis/                            the scripts named in Appendix A.3
  derived/                             per-unit tables behind Tables 6, 10, 11 and 12
  capture/                             the scripts that drove the D435 and the arm
  templates/                           the caliper sheet templates of Section 4.4
  analysis/out/                        the CSV that Appendix A.3 regenerates
```

## Regenerating Section 5

```bash
python analysis/01_selective_risk_split.py --root evidence/CSV/SCI_RESTART_20261008
```

Reads `SCI_STAGE08_P1_CONTINUOUS_E1/results/SELECTIVE_RISK_CONTINUOUS.csv` and
`p1_eval_table.csv`, writes `analysis/out/selective_risk_by_family.csv`, and prints
the two-regime table used in the paper. The script asserts the reported bounds and
fails loudly if a value moves.

## Regenerating the uncertainty budget of Section 4.4

```bash
python analysis/02_metrology_u95.py --dir .
```

Reads `templates/part_thickness_survey.csv` and
`templates/reference_step_readings.csv`. With no calibration certificate the
expanded uncertainty is written as `UNKNOWN` rather than filled in — that behaviour
is deliberate and is the point of Section 4.4.

## The per-unit tables

| file | what it holds | used by |
|---|---|---|
| `derived/measured_step_error.csv` | caliper reference and signed bias $e_h$ per placement unit | Table 6, Sections 6.2–6.5 |
| `derived/r3a_results.csv` | the reduction behind Table 6 | Section 6 |
| `derived/graspness_per_unit.csv` | GSNet graspness statistics per unit, from the frozen weights | Table 10, Section 7.2 |
| `derived/joined.csv` | graspness joined with the measured bias | Table 10 |
| `derived/expC_live2.csv` | the three single-frame statistics, session 1 (archived definition) | Table 12 |
| `derived/expC_features_definition_A.csv` | same, hole-filled inlier ROI | Table 12 |
| `derived/expC_features_definition_B.csv` | same, convex-hull ROI | Table 12 |

The three `expC_*` files are what Section 7.5 is about: the valid-fraction
coefficient changes sign between them, and that is the finding.

## What is deliberately absent

The GSNet checkpoint itself is not redistributed here. Its identity is pinned by
SHA-256 `a0b9d85b300e40c76b66d092de62138d74757d6b7c2037f0d364f33960c54aa9`
(184,429,769 bytes) and the upstream project should be cited for the weights.
