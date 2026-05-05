# Data Quality Report

## Quality Summary
- Completeness: 0 missing values across the raw CSV.
- Consistency: 3,093 duplicate rows detected in the raw CSV.
- Accuracy: validation rules enforce allowed stage labels, non-negative processing times, and bounded family/priority values.
- Timeliness: no direct timestamp field exists, so timeliness is interpreted as batch freshness and the presence of a complete closed-job record.
- Structural check: all required validation columns are present.

## Validation Rules Applied
- Categorical values for stage labels must match the allowed manufacturing codes in `src/data/data_validation.py`.
- `S1_efficiency` and `S2_efficiency` must be non-zero for mandatory stages.
- `S3_efficiency` and `S4_efficiency` may be zero only when the corresponding stage is skipped.
- `stage_time_range`, `stage_time_std`, `Priority`, `queue_pressure`, and `Processing_Time_*` values must remain non-negative and finite.

## Interpretation
- The raw dataset is structurally complete and ready for feature engineering.
- Quality issues, if any, are easiest to inspect through the generated validation logs in `Logger/`.
- Timeliness cannot be measured as latency, so the dataset should be treated as a snapshot of already completed manufacturing jobs.
