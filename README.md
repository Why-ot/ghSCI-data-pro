# ghSCI-data-pro

Material for *Reference-Graded Characterisation of an Active-Stereo Depth Sensor*.

```
parts/            the raw captures, split into 30 MB archives
repro/            everything needed to regenerate the numbers in the paper
expC_features/    the first deposit of the per-unit feature tables (kept for continuity)
```

## parts/ — raw captures

| archive | units | frames/unit | what it holds |
|---|---:|---:|---|
| `depth_all.tar` | 128 | 30 | Z16 depth frames (millimetres) + `meta.json` with intrinsics |
| `color_all.tar` | 128 | 30 | BGR8 colour frames |

Of the 128 directories, 120 are analysis units and 8 are rejected or test captures
kept for audit.

| dataset | units | standoff |
|---|---:|---|
| `live2` | 30 | 355 mm (re-placed, session 1) |
| `live3` | 30 | 355 mm (re-placed, session 2) |
| `live_repeat` | 30 | 355 mm (fixed-placement control) |
| `live4_d350` | 15 | 376 mm |
| `live4_d450` | 15 | 448 mm |

Camera: Intel RealSense D435, serial 342222072464, firmware 5.13.0.55.

The archives are split because GitHub rejects files above 100 MB. Reassemble with:

```bash
cat parts/depth_all.tar.part_* > depth_all.tar
cat parts/color_all.tar.part_* > color_all.tar
```

Checksums of the whole archives:

```
1ef3d238cd8ea3a2e2c29aa4dacaf93b27f145d3f6e6fda22b9f7f4a3e4d1c2c  depth_all.tar
a28b2ef2b9d8195e4b69b30fae5da45a4ca12d2c52cb466c74a020ccd2889f3e  color_all.tar
```

## repro/ — regenerating the numbers

| folder | contents |
|---|---|
| `repro/evidence/` | the frozen per-scene and per-candidate tables of Section 5 |
| `repro/analysis/` | the scripts named in Appendix A.3, and the CSV they regenerate |
| `repro/derived/` | per-unit tables behind Tables 6, 10, 11 and 12 |
| `repro/capture/` | the scripts that drove the camera and the arm |
| `repro/templates/` | the caliper sheet templates of Section 4.4 |

```bash
python repro/analysis/01_selective_risk_split.py --root repro/evidence/CSV/SCI_RESTART_20261008
python repro/analysis/02_metrology_u95.py --dir repro
```

`repro/derived/expC_*.csv` are the three definitions of the region of interest that
Section 7.5 compares. The valid-fraction coefficient changes sign between them; that
is the finding, not an artefact of the deposit.

## Not included

The grasp detector weights are not redistributed. Their identity is pinned by
SHA-256 `a0b9d85b300e40c76b66d092de62138d74757d6b7c2037f0d364f33960c54aa9`
(184,429,769 bytes, epoch 10, 216 tensors); cite the upstream GraspNet project for
the checkpoint itself.
