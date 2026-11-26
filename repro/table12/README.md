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
`_join/joined.csv`, not from the ten-draw ensemble used for Tables 3-6. The difference
between the two estimators is not uniform across units. Over the same 90 units:

| statistic | value |
|---|---|
| mean absolute difference | 0.298 mm |
| median absolute difference | 0.105 mm |
| maximum absolute difference | 3.442 mm |
| mean absolute difference, 448 mm group only | 1.446 mm |

Most units agree closely; a few at the largest standoff differ by millimetres, and
those few carry enough leverage to move the pooled coefficient:

| estimator | pooled | within target |
|---|---|---|
| single frozen realisation (this file) | -0.462 | -0.074 |
| ten-draw ensemble mean | -0.377 | -0.053 |

Both are negative pooled and both collapse to near zero once each target's mean is
removed, so the qualitative reading does not depend on which estimator is used.
Table 12 uses the frozen realisation, and that file is deposited here so the
coefficient does not depend on which table a reader picks up.
## Permutation p values

`permutation_pvalues.py` computes the p column of the graspness table the way the
manuscript caption describes: one variable permuted, 100,000 permutations, seed
20261126, two-sided, `p = (1 + #{|rho_perm| >= |rho_obs|}) / (1 + N)`.

    python permutation_pvalues.py

The analytic p from `reproduce_table12.py` (scipy's t approximation) is close but
not identical, so the two must not be mixed in one table. The Monte-Carlo standard
error is about 0.0016 at p = 0.5 and 0.0005 at p = 0.05, which is why the table
quotes two decimals.
