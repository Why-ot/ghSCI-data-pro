# The caliper reference tables are not published here

Two files that used to sit in this directory have been removed:

* `reference_steps.csv`
* `reference_repeatability.csv`

They were written by `08_reference_check.py` from a partially transcribed caliper
sheet, and their values do not correspond to the caliper reference the paper uses:

| quantity | removed file | value used in the paper |
|---|---|---|
| S20 step | 20.125 mm | 19.96 mm |
| S40-A step | 40.079 mm | 39.97 mm |
| S40-B step | 40.213 mm | 39.98 mm |
| S60 step | 60.153 mm | 59.97 mm |
| S00 thickness | 21.0 mm | 6 mm base plate |

Leaving them here invited a reader to recompute a table and get a different answer,
which is the opposite of what this repository is for.

The readings behind the reference values in use were taken on paper and were never
digitised, so no file in this repository can reproduce them. What is available instead:

* the five reference values themselves, in Table 3 of the paper and as `REF` in
  `../../step_height/measure_eh.py`;
* a digitisation template and the values in use, in `../../metrology/`;
* the repeatability that bounds them, stated in Section 5.3 of the paper and derived
  from four readings per quantity;
* the per-unit step measurements, in `../derived/measured_step_error.csv` and
  `../../step_height/ensemble_per_unit.csv`.

`08_reference_check.py` is left in place. Pointed at a complete sheet it will reproduce
the reduction, and that remains the correct way to check the reference if the paper
sheet is ever transcribed.

The two files remain in the git history at commit `e5ba35f`. They are not reachable
from the current tree, but they are not erased either; anyone reading the history will
find them, and this note is here so that they find the explanation with them.
