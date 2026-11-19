# The caliper reference tables are not published here

Two files that used to sit in this directory have been removed:

* `reference_steps.csv`
* `reference_repeatability.csv`

They were written by `08_reference_check.py` from the 21 mm-base trial batch, before
the staircase targets were measured, and their values do not correspond to the
caliper reference the paper uses:

| quantity | removed file | value used in the paper |
|---|---|---|
| S20 step | 20.125 mm | 19.96 mm |
| S40-A step | 40.079 mm | 39.97 mm |
| S40-B step | 40.213 mm | 39.98 mm |
| S60 step | 60.153 mm | 59.97 mm |
| S00 thickness | 21.0 mm | 6 mm base plate |

Leaving them here invited a reader to recompute a table and get a different answer,
which is the opposite of what this repository is for.

The readings behind the reference values in use were taken on paper and are now
transcribed in `../../metrology/reference_readings.csv`, one row per target,
orientation, measurand and position; `../../metrology/derive_reference.py` reproduces
the five values from them. What that file does and does not carry:

* S20, S40-B and S60 have all eight individual readings each, so both their means and
  their standard deviations reproduce (0.028, 0.010 and 0.013 mm respectively);
* S40-A is recorded as the mean of each orientation's four readings, so its reference
  value reproduces but its spread does not and is carried from the paper sheet;
* S00 is a single reported plate thickness.

The five values themselves are also in Table 3 of the paper and as `REF` in
`../../step_height/measure_eh.py`. An empty digitisation template remains in
`../../metrology/` for anyone who wants to re-enter the sheet by hand.

`08_reference_check.py` is left in place. Pointed at a complete sheet it reproduces the
reduction, and remains the correct way to check a future measurement session.

The two files remain in the git history at commit `e5ba35f`. They are not reachable
from the current tree, but they are not erased either; anyone reading the history will
find them, and this note is here so that they find the explanation with them.
