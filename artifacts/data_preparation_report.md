# Data Preparation Report

## Feature Engineering
- `S1_efficiency` to `S4_efficiency`: stage processing efficiency derived from processing time divided by elapsed stage duration.
- `stage_time_std`: variability across the four stage processing times.
- `stage_time_range`: max-minus-min spread across stage processing times.
- `queue_pressure`: proxy for how much work was queued before the job entered the line.

## Activities Performed
- Removed duplicate raw records before computing the final processed dataset.
- Computed stage-level efficiency and cross-stage variability features.
- Ran a correlation check against the offline breakdown label for feature review.
- Dropped leakage-prone and post-job fields before saving the processed output.

## Leakage Controls
- Removed fields such as `BREAKS`, `BREAKDOWN`, `Anomaly_identification`, `Overall_processing_time`, `Overall_waiting_time`, and `Tardiness` from the processed output.
- Retained only pre-breakdown or safe retrospective features for modeling.

## Output
- Processed dataset path: `data_source/Processed/processed_manufacturing.csv`
- Processed dataset shape: 14,412 rows and 17 columns
- Processed output columns retained: 17

## Conclusion
- The preparation pipeline produces a leakage-aware modeling table with engineered operational signals.
- The strongest value is expected from variability features and stage efficiencies rather than raw identifiers.
- Source pipeline handles: ID, Start_time_S1, Finish_time_S1, Start_time_S2, Finish_Time_S2, Start_time_S3, Finish_time_S3, Start_time_s4, Finish_time, Overall_processing_time, Overall_waiting_time, Tardiness, BREAKS.
