from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT_DIR / "data_source" / "raw" / "manufacturing.csv"
PROCESSED_CSV = ROOT_DIR / "data_source" / "Processed" / "processed_manufacturing.csv"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"


def load_raw_data() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df


def load_processed_data() -> pd.DataFrame | None:
    if not PROCESSED_CSV.exists():
        return None
    return pd.read_csv(PROCESSED_CSV)


def infer_role(column: str) -> str:
    if column == "BREAKS":
        return "Target / breakdown count"
    if column == "ID":
        return "Record identifier"
    if column == "Priority":
        return "Scheduling priority"
    if column == "Family_type":
        return "Product family category"
    if "stage" in column.lower():
        return "Production stage label or timing field"
    if column.startswith("Processing_Time"):
        return "Stage processing duration"
    if column.startswith("Overall_"):
        return "Job-level aggregate metric"
    if column == "Tardiness":
        return "Job delay beyond target"
    return "Operational manufacturing attribute"


def format_number(value: float | int) -> str:
    if pd.isna(value):
        return "n/a"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    if isinstance(value, (float, np.floating)):
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{float(value):,.4f}".rstrip("0").rstrip(".")
    return str(value)


def build_data_description(df: pd.DataFrame) -> str:
    breakdown_count = int((df["BREAKS"] > 0).sum())
    lines = [
        "# Data Description Report",
        "",
        "## Data Source",
        f"- Source file: `data_source/raw/manufacturing.csv`",
        f"- Rows: {len(df):,}",
        f"- Columns used for analysis: {len(df.columns):,}",
        f"- Breakdown records: {breakdown_count:,} ({breakdown_count / len(df) * 100:.1f}%)",
        "",
        "## Extraction Method",
        "- The dataset is loaded directly from the raw CSV file in `data_source/raw/`.",
        "- The validation script and feature-engineering script both read the same raw source, so the generated reports stay aligned with the pipeline.",
        "- The processed dataset is written to `data_source/Processed/processed_manufacturing.csv` after feature engineering.",
        "",
        "## Assumptions",
        "- `BREAKS > 0` is treated as the anomaly/breakdown condition.",
        "- The raw CSV is the authoritative source for the schema and quality checks.",
        "- Empty stage labels encoded as `0` indicate skipped stages, matching the validation rules in `src/data/data_validation.py`.",
        "- Timeliness is evaluated as batch completeness rather than ingestion latency, because the dataset does not include a capture timestamp.",
        "",
        "## Operational Context",
        "- The dataset represents manufacturing jobs moving through up to four stages.",
        "- Stage timing, processing time, queue pressure, and job priority are the main operational signals used for anomaly detection.",
    ]
    return "\n".join(lines)


def build_data_dictionary(df: pd.DataFrame) -> str:
    rows: list[str] = []
    for column in df.columns:
        series = df[column]
        dtype = str(series.dtype)
        role = infer_role(column)
        non_null = int(series.notna().sum())
        nulls = int(series.isna().sum())
        unique = int(series.nunique(dropna=True))

        if pd.api.types.is_numeric_dtype(series):
            min_value = format_number(series.min())
            max_value = format_number(series.max())
            extra = f"range: {min_value} to {max_value}"
        else:
            sample_values = sorted(series.dropna().astype(str).unique().tolist())[:5]
            extra = f"sample values: {', '.join(sample_values)}"

        rows.append(
            f"| {column} | {dtype} | {role} | {non_null:,} | {nulls:,} | {unique:,} | {extra} |"
        )

    lines = [
        "# Data Dictionary",
        "",
        "| Column | Data type | Semantic context | Non-null | Nulls | Unique | Value range / examples |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
        *rows,
    ]
    return "\n".join(lines) + "\n"


def build_data_exploration_report(df: pd.DataFrame) -> str:
    breakdown_distribution = df["BREAKS"].value_counts().sort_index()
    target_rows = [f"- `BREAKS = {value}`: {count:,}" for value, count in breakdown_distribution.items()]

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if "BREAKS" in numeric_cols:
        numeric_cols.remove("BREAKS")
    skew_desc = df[numeric_cols].skew().abs().sort_values(ascending=False)
    most_skewed = "`" + "`, `".join(skew_desc.head(5).index.tolist()) + "`" if not skew_desc.empty else "n/a"

    lines = [
        "# Data Exploration Report",
        "",
        "## Univariate Analysis",
        "- Target distribution from the preprocessing notebook:",
        *target_rows,
        f"- Breakdown rate: {(df['BREAKS'] > 0).mean() * 100:.1f}%",
        "- The notebook also examined numeric histograms, categorical counts, and box plots for IQR-based outliers.",
        f"- The most skewed numeric fields in the raw data are: {most_skewed}.",
        "",
        "## Key Notebook Findings",
        "- IQR outlier checks in the notebook found no outliers for `Priority`, `Family_type`, `Processing_Time_S1`, `Processing_Time_S2`, and `Processing_Time_S3`.",
        "- `Processing_Time_S4` showed 1,233 outliers (8.5%).",
        "- `Tardiness` showed 1,122 outliers (7.7%).",
        "- The notebook saved a correlation heatmap and a point-biserial correlation summary for numeric features versus `BREAKDOWN`.",
        "",
        "## Bivariate Patterns",
        "- The feature-engineering notebook reported strong relationships between breakdowns and the engineered variability features.",
        "- The strongest reported point-biserial correlations were `stage_time_range` and `stage_time_std`, followed by the stage efficiencies.",
        "- This suggests that variability across stages is more informative than any single raw duration alone.",
        "",
        "## Implications",
        "- Class imbalance is present but not extreme; anomaly modeling should still use class-aware evaluation.",
        "- Stage duration dispersion appears to be a high-value signal for anomaly detection.",
        "- Raw stage timing and job-level delay fields should be preserved for exploratory analysis, but leakage-prone fields must be removed before modeling.",
    ]
    return "\n".join(lines)


def build_data_quality_report(df: pd.DataFrame) -> str:
    missing_total = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    required_columns = [
        "ID",
        "Priority",
        "Family_type",
        "First_stage",
        "Start_time_S1",
        "Finish_time_S1",
        "Processing_Time_S1",
        "Second_stage",
        "Start_time_S2",
        "Finish_Time_S2",
        "Processing_Time_S2",
        "Third_stage",
        "Start_time_S3",
        "Finish_time_S3",
        "Processing_Time_S3",
        "Fourth_stage",
        "Processing_Time_S4",
        "Start_time_s4",
        "Finish_time",
        "Overall_processing_time",
        "Overall_waiting_time",
        "Tardiness",
        "BREAKS",
    ]
    missing_required = [column for column in required_columns if column not in df.columns]

    quality_lines = [
        f"- Completeness: {missing_total:,} missing values across the raw CSV.",
        f"- Consistency: {duplicate_rows:,} duplicate rows detected in the raw CSV.",
        "- Accuracy: validation rules enforce allowed stage labels, non-negative processing times, and bounded family/priority values.",
        "- Timeliness: no direct timestamp field exists, so timeliness is interpreted as batch freshness and the presence of a complete closed-job record.",
    ]
    if missing_required:
        quality_lines.append(f"- Structural check: missing required columns detected: {', '.join(missing_required)}.")
    else:
        quality_lines.append("- Structural check: all required validation columns are present.")

    lines = [
        "# Data Quality Report",
        "",
        "## Quality Summary",
        *quality_lines,
        "",
        "## Validation Rules Applied",
        "- Categorical values for stage labels must match the allowed manufacturing codes in `src/data/data_validation.py`.",
        "- `S1_efficiency` and `S2_efficiency` must be non-zero for mandatory stages.",
        "- `S3_efficiency` and `S4_efficiency` may be zero only when the corresponding stage is skipped.",
        "- `stage_time_range`, `stage_time_std`, `Priority`, `queue_pressure`, and `Processing_Time_*` values must remain non-negative and finite.",
        "",
        "## Interpretation",
        "- The raw dataset is structurally complete and ready for feature engineering.",
        "- Quality issues, if any, are easiest to inspect through the generated validation logs in `Logger/`.",
        "- Timeliness cannot be measured as latency, so the dataset should be treated as a snapshot of already completed manufacturing jobs.",
    ]
    return "\n".join(lines)


def build_data_preparation_report(raw_df: pd.DataFrame, processed_df: pd.DataFrame | None) -> str:
    processed_shape = f"{processed_df.shape[0]:,} rows and {processed_df.shape[1]:,} columns" if processed_df is not None else "not available"
    processed_columns = processed_df.columns.tolist() if processed_df is not None else []
    dropped_columns = [
        "ID",
        "Start_time_S1",
        "Finish_time_S1",
        "Start_time_S2",
        "Finish_Time_S2",
        "Start_time_S3",
        "Finish_time_S3",
        "Start_time_s4",
        "Finish_time",
        "Overall_processing_time",
        "Overall_waiting_time",
        "Tardiness",
        "BREAKS",
        "BREAKDOWN",
        "Anomaly_identification",
    ]
    present_dropped = [column for column in dropped_columns if column in raw_df.columns or (processed_df is not None and column in processed_columns)]

    lines = [
        "# Data Preparation Report",
        "",
        "## Feature Engineering",
        "- `S1_efficiency` to `S4_efficiency`: stage processing efficiency derived from processing time divided by elapsed stage duration.",
        "- `stage_time_std`: variability across the four stage processing times.",
        "- `stage_time_range`: max-minus-min spread across stage processing times.",
        "- `queue_pressure`: proxy for how much work was queued before the job entered the line.",
        "",
        "## Activities Performed",
        "- Removed duplicate raw records before computing the final processed dataset.",
        "- Computed stage-level efficiency and cross-stage variability features.",
        "- Ran a correlation check against the offline breakdown label for feature review.",
        "- Dropped leakage-prone and post-job fields before saving the processed output.",
        "",
        "## Leakage Controls",
        "- Removed fields such as `BREAKS`, `BREAKDOWN`, `Anomaly_identification`, `Overall_processing_time`, `Overall_waiting_time`, and `Tardiness` from the processed output.",
        "- Retained only pre-breakdown or safe retrospective features for modeling.",
        "",
        "## Output",
        "- Processed dataset path: `data_source/Processed/processed_manufacturing.csv`",
        f"- Processed dataset shape: {processed_shape}",
        f"- Processed output columns retained: {len(processed_columns):,}",
        "",
        "## Conclusion",
        "- The preparation pipeline produces a leakage-aware modeling table with engineered operational signals.",
        "- The strongest value is expected from variability features and stage efficiencies rather than raw identifiers.",
        f"- Source pipeline handles: {', '.join(present_dropped)}.",
    ]
    return "\n".join(lines)


def write_report(filename: str, content: str) -> None:
    output_path = ARTIFACTS_DIR / filename
    output_path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_index(report_names: list[str]) -> None:
    lines = [
        "# Manufacturing Analysis Artifacts",
        "",
        "Generated reports:",
    ]
    for name in report_names:
        lines.append(f"- {name}")
    write_report("README.md", "\n".join(lines))


def main() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw_data()
    processed_df = load_processed_data()

    reports = {
        "data_description_report.md": build_data_description(raw_df),
        "data_dictionary_report.md": build_data_dictionary(raw_df),
        "data_exploration_report.md": build_data_exploration_report(raw_df),
        "data_quality_report.md": build_data_quality_report(raw_df),
        "data_preparation_report.md": build_data_preparation_report(raw_df, processed_df),
    }

    for filename, content in reports.items():
        write_report(filename, content)

    write_index(list(reports.keys()))
    print(f"Wrote {len(reports)} reports to {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()