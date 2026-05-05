# Data Description Report

## Data Source
- Source file: `data_source/raw/manufacturing.csv`
- Rows: 17,600
- Columns used for analysis: 23
- Breakdown records: 5,268 (29.9%)

## Extraction Method
- The dataset is loaded directly from the raw CSV file in `data_source/raw/`.
- The validation script and feature-engineering script both read the same raw source, so the generated reports stay aligned with the pipeline.
- The processed dataset is written to `data_source/Processed/processed_manufacturing.csv` after feature engineering.

## Assumptions
- `BREAKS > 0` is treated as the anomaly/breakdown condition.
- The raw CSV is the authoritative source for the schema and quality checks.
- Empty stage labels encoded as `0` indicate skipped stages, matching the validation rules in `src/data/data_validation.py`.
- Timeliness is evaluated as batch completeness rather than ingestion latency, because the dataset does not include a capture timestamp.

## Operational Context
- The dataset represents manufacturing jobs moving through up to four stages.
- Stage timing, processing time, queue pressure, and job priority are the main operational signals used for anomaly detection.
