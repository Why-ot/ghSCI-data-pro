# Table 12 inputs and script

`table12_inputs.csv` holds the 90 rows that Table 12 of the manuscript is computed
from: median graspness of each unit's support region against that unit's signed
step bias. The flat control and the five S40-A units at 376 mm whose segmentation
failed are excluded.

`reproduce_table12.py` regenerates every coefficient in the table, rho and
two-sided p, using `scipy.stats.spearmanr`:

    python reproduce_table12.py

Tested with scipy 1.18.1. The p-value follows scipy's t approximation with n-2
degrees of freedom.

## Why these values differ from an earlier calculation

The step heights in `table12_inputs.csv` come from the single frozen realisation in
`_join/joined.csv`, not from the ten-draw ensemble used for Tables 3-6. The two
differ by a few hundredths of a millimetre per unit, which moves the pooled
coefficient between about -0.38 and -0.46:

| estimator | pooled | within target |
|---|---|---|
| single frozen realisation (this file) | -0.462 | -0.074 |
| ten-draw ensemble mean | -0.377 | -0.053 |

Both are negative pooled and both collapse to near zero once each target's mean is
removed, so the qualitative reading does not depend on which estimator is used.
Table 12 uses the frozen realisation, and that file is deposited here so the
coefficient does not depend on which table a reader picks up.