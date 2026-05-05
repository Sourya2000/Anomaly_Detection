# Data Exploration Report

## Univariate Analysis
- Target distribution from the preprocessing notebook:
- `BREAKS = 0`: 12,332
- `BREAKS = 1`: 4,199
- `BREAKS = 2`: 1,054
- `BREAKS = 3`: 15
- Breakdown rate: 29.9%
- The notebook also examined numeric histograms, categorical counts, and box plots for IQR-based outliers.
- The most skewed numeric fields in the raw data are: `Tardiness`, `Processing_Time_S4`, `Processing_Time_S3`, `Processing_Time_S2`, `Processing_Time_S1`.

## Key Notebook Findings
- IQR outlier checks in the notebook found no outliers for `Priority`, `Family_type`, `Processing_Time_S1`, `Processing_Time_S2`, and `Processing_Time_S3`.
- `Processing_Time_S4` showed 1,233 outliers (8.5%).
- `Tardiness` showed 1,122 outliers (7.7%).
- The notebook saved a correlation heatmap and a point-biserial correlation summary for numeric features versus `BREAKDOWN`.

## Bivariate Patterns
- The feature-engineering notebook reported strong relationships between breakdowns and the engineered variability features.
- The strongest reported point-biserial correlations were `stage_time_range` and `stage_time_std`, followed by the stage efficiencies.
- This suggests that variability across stages is more informative than any single raw duration alone.

## Implications
- Class imbalance is present but not extreme; anomaly modeling should still use class-aware evaluation.
- Stage duration dispersion appears to be a high-value signal for anomaly detection.
- Raw stage timing and job-level delay fields should be preserved for exploratory analysis, but leakage-prone fields must be removed before modeling.
