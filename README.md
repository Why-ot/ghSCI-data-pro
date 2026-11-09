# ghSCI-data-pro

Raw depth and colour captures for *Reference-Graded Characterisation of an
Active-Stereo Depth Sensor*.

## Contents

| archive | units | frames/unit | what it holds |
|---|---:|---:|---|
| `depth_all.tar` | 128 | 30 | Z16 depth frames (millimetres) + `meta.json` with intrinsics |
| `color_all.tar` | 128 | 30 | BGR8 colour frames |

Of the 128 directories, 120 are analysis units and 8 are rejected or test
captures kept for audit.

## Datasets inside the archives

| dataset | units | standoff |
|---|---:|---|
| `live2` | 30 | 355 mm (re-placed, session 1) |
| `live3` | 30 | 355 mm (re-placed, session 2) |
| `live_repeat` | 30 | 355 mm (fixed-placement control) |
| `live4_d350` | 15 | 376 mm |
| `live4_d450` | 15 | 448 mm |

Camera: Intel RealSense D435, serial 342222072464, firmware 5.13.0.55.

## Why the files are split

GitHub rejects files above 100 MB, so each archive is stored as 30 MB parts.
Reassemble with:

```bash
cat depth_all.tar.part_* > depth_all.tar
cat color_all.tar.part_* > color_all.tar
```

Checksums of the whole archives:

```
1ef3d238cd8ea3a2e2c29aa4dacaf93b27f145d3f6e6fda22b9f7f4a3e4d1c2c  depth_all.tar
a28b2ef2b9d8195e4b69b30fae5da45a4ca12d2c52cb466c74a020ccd2889f3e  color_all.tar
```
