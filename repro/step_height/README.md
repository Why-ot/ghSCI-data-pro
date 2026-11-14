# Step-height reduction

The code that produces Tables 7, 8 and 9 of the paper, and the per-unit table it
produces. This is the part of the analysis that turns 3,840 depth frames into 60
step-height measurements; everything downstream of it (bias, spread, correlations)
is arithmetic on the files here.

## What it does

For each placement unit:

1. stack the 30 depth frames and take the per-pixel median;
2. back-project to camera coordinates with the intrinsics in `meta.json`;
3. find horizontal planes by sequential RANSAC (`|n_z| > 0.95`, tolerance 1.5 mm,
   800 iterations per plane, up to 8 planes);
4. locate the low face at `table_depth - anchor` and take the highest supported plane
   below it as the raised face;
5. report `step = low_face_depth - high_face_depth`.

## Two choices that move the numbers

Both are stated in the paper (Sections 6.1 and 8) because each one is larger than the
reproducibility figure.

**Anchor.** The base-plate thickness is a *measured* quantity, not an assumed one:
it is the camera's own reading of the 6 mm plate. At the nominal standoff that reading
is 5.85 mm, and it is reused for every session captured at 355 mm; only a change of
standoff requires re-measuring it from that standoff's flat-control units. Anchoring
each session separately instead shifts every stepped target by about 0.3 mm — the size
of the effect being measured.

```python
FIXED_ANCHOR_AT = {"live2": 5.85, "live3": 5.85, "live_repeat": 5.85}
```

**Aggregation.** The reported statistic is the mean over placement units, as
Equation (6) defines it. The median differs from it by up to 0.23 mm in the cell with
the widest placement spread.

## Reproducibility

The plane fit draws a random sample, so a single run is one realisation. Ten
independent draws, aggregated by the mean with the anchor policy above, reproduce
every entry of Tables 7 and 8 and the first three rows of Table 9 to within
**0.11 mm**. The 448 mm row of Table 9 moves by 0.64 mm between draws and is discussed
where it is used.

The seed is derived from the unit name by SHA-256, so a run is repeatable on any
machine; `SEED_OFFSET` perturbs it to generate the ensemble.

## Running it

Input layout expected — one directory per dataset, one sub-directory per unit:

```
_r3a_for_pc/
  live2/S60_0deg_P01/{depth_raw/*.png, meta.json}
  live3/...
  live4_d350/  live4_d450/  live_repeat/
```

Unpack `parts/depth_all.tar` from this repository to get exactly that tree.

```bash
python measure_eh.py             # one draw -> measured_eh.csv
python run_ensemble.py           # ten draws -> ensemble/ensemble_per_unit.csv
python make_tables.py            # print Tables 7, 8, 9 from the ensemble
```

`run_ensemble.py` takes about 35 minutes on a laptop (ten draws of 120 units).

## Files

| file | role |
|---|---|
| `measure_eh.py` | the reduction; writes one row per unit |
| `run_ensemble.py` | ten draws with different seeds, combined per unit |
| `make_tables.py` | aggregates the ensemble into the three tables |
| `ensemble/ensemble_per_unit.csv` | per-unit value and its spread across the ten draws |

`ensemble_per_unit.csv` is the file to check a table entry against.
