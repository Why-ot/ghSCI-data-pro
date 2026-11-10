# MANIFEST — R3-A capture backup (2026-11-09)

Location: `C:\Users\lqx\Desktop\论文\DATA_BACKUP_20261109\`
Transferred from: Jetson `yuanyou@192.168.31.230:/home/yuanyou/R3A_CAPTURE` over LAN (802.11, ~0.14-0.23 MB/s).

## Archives

| file | bytes | sha256 |
|---|---:|---|
| `depth_all.tar` | 355,635,200 | `1ef3d238cd8ea3a2e2c29aa4dacaf93b27f145d3f6e6fda22b9f7f4a3e4d1c2c` |
| `color_all.tar` | 981,964,800 | `a28b2ef2b9d8195e4b69b30fae5da45a4ca12d2c52cb466c74a020ccd2889f3e` |

Both verified against the source checksums after transfer.

## Contents

- 128 directories, 30 frames each, 3840 depth PNGs (Z16, millimetres) + 3840 colour PNGs
- 120 are analysis units; 8 are rejected or test captures kept for audit
- 128 `meta.json` with intrinsics (depth archive)

| dataset | units |
|---|---:|
| `live_repeat` | 30 (plus 6 `*_REJECT_*` and 2 `TEST_*`, excluded) |
| `live2` | 30 |
| `live3` | 30 |
| `live4_d350` | 15 |
| `live4_d450` | 15 |


## Units worth noting

- `live2` and `live3` are the two re-placed sessions (5 S00, 5 S20, 5 S40A-0deg, 5 S40A-180deg, 5 S40B, 5 S60 each).
- `live_repeat` is the fixed-placement recapture control.
- `live4_d350` (376 mm) and `live4_d450` (448 mm) are the standoff sweep; their `S40A_*` directories actually contain the flat S00 part and are excluded in the analysis.

## Camera

Intel RealSense D435, serial 342222072464, firmware 5.13.0.55, 848x480 depth, 30 frames per unit.

## Also in this folder

Analysis outputs (`r3a_results.csv`, `expC_*.csv`), five arm-pose records (`pose_*.json`), and the capture/segmentation scripts (`live_preview.py`, `seg_step.py`, `plane_check.py`, `readboth.py`, ...).

