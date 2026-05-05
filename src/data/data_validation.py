"""
Raw Data Validation
===================
Validates the raw manufacturing.csv before feature engineering.
All issues are saved to the Logger/ folder as CSV files + a summary log.

Usage:
    python data_validation.py

Logger/ outputs:
    Logger/validation_summary.log       — human-readable run report
    Logger/duplicate_rows.csv           — duplicate row records
    Logger/missing_values.csv           — columns with null counts
    Logger/invalid_categoricals.csv     — unexpected categorical values
    Logger/processing_time_negative.csv — negative processing times
    Logger/family_type_out_of_range.csv — Family_type outside [1, 40]
    Logger/priority_queue_invalid.csv   — invalid Priority values
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV  = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data_source/raw/manufacturing.csv"))
LOG_DIR    = os.path.abspath(os.path.join(SCRIPT_DIR, "../../Logger"))
os.makedirs(LOG_DIR, exist_ok=True)

# ── Logging setup ─────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(LOG_DIR, "validation_summary.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def save_issues(df_issues: pd.DataFrame, filename: str, label: str):
    """Save a dataframe of bad rows to the Logger folder and log the event."""
    if df_issues.empty:
        log.info("PASS  %-45s  0 rows affected.", label)
        return
    path = os.path.join(LOG_DIR, filename)
    df_issues.to_csv(path, index=False)
    log.warning("FAIL  %-45s  %d rows  ->  %s", label, len(df_issues), path)


# ── Load ──────────────────────────────────────────────────────────────────────
log.info("=" * 65)
log.info("RAW DATA VALIDATION")
log.info("Input : %s", INPUT_CSV)
log.info("Logger: %s/", LOG_DIR)
log.info("=" * 65)

df = pd.read_csv(INPUT_CSV)
log.info("Loaded dataset — rows: %d, columns: %d", *df.shape)

# ── VALIDATE REQUIRED COLUMNS EXIST ──────────────────────────────────────────
required_cols = {
    "ID", "Priority", "Family_type",
    "First_stage", "Start_time_S1", "Finish_time_S1", "Processing_Time_S1",
    "Second_stage", "Start_time_S2", "Finish_Time_S2", "Processing_Time_S2",
    "Third_stage", "Start_time_S3", "Finish_time_S3", "Processing_Time_S3",
    "Fourth_stage", "Start_time_s4", "Finish_time", "Processing_Time_S4",
    "Overall_processing_time", "Overall_waiting_time", "Tardiness", "BREAKS",
}
missing_cols = required_cols - set(df.columns)
if missing_cols:
    log.error("CRITICAL: Missing required columns: %s", missing_cols)
    log.error("Available columns: %s", sorted(df.columns.tolist()))
    sys.exit(1)


# ── 1. MISSING VALUES ────────────────────────────────────────────────────────
log.info("\n--- [1] Missing Values ---")
null_series = df.isnull().sum()
null_cols   = null_series[null_series > 0]
if null_cols.empty:
    log.info("PASS  No missing values in any column.")
else:
    missing_df = pd.DataFrame({
        "column":    null_cols.index,
        "null_count": null_cols.values,
        "null_pct":  (null_cols.values / len(df) * 100).round(2),
    })
    save_issues(missing_df, "missing_values.csv", "Missing Values")


# ── 2. DUPLICATE ROWS ────────────────────────────────────────────────────────
log.info("\n--- [2] Duplicate Rows ---")
dup_mask = df.duplicated(keep=False)
save_issues(df[dup_mask].copy(), "duplicate_rows.csv", "Duplicate Rows")


# ── 3. CATEGORICAL ALLOWED VALUES ────────────────────────────────────────────
log.info("\n--- [3] Categorical Allowed Values ---")
allowed = {
    "First_stage":  {"SMD_0", "SMD_1", "SMD_2", "SMD_3", "SMD_4"},
    "Second_stage": {"AOI_0", "AOI_1", "AOI_2", "AOI_3", "AOI_4"},
    "Third_stage":  {"SS_0",  "SS_1",  "SS_2",  "SS_3",  "SS_4", "0"},
    "Fourth_stage": {"CC_0",  "CC_1",  "0"},
}
invalid_cat_frames = []
for col, valid_set in allowed.items():
    mask = ~df[col].astype(str).isin(valid_set)
    if mask.any():
        bad = df[mask].copy()
        bad["_invalid_column"] = col
        bad["_invalid_value"]  = df.loc[mask, col]
        invalid_cat_frames.append(bad)
        log.warning("FAIL  '%s' has unexpected values: %s", col, set(df.loc[mask, col].unique()))

if invalid_cat_frames:
    save_issues(pd.concat(invalid_cat_frames), "invalid_categoricals.csv", "Invalid Categorical Values")
else:
    log.info("PASS  %-45s  all columns clean.", "Categorical Allowed Values")


# ── 4. PROCESSING TIMES ─────────────────────────────────────────────────────────
log.info("\n--- [5] Processing Times (non-negative) ---")
processing_cols = ["Processing_Time_S1", "Processing_Time_S2", "Processing_Time_S3", "Processing_Time_S4"]
proc_bad = pd.Series(False, index=df.index)
for col in processing_cols:
    proc_bad |= (df[col] < 0) | (~np.isfinite(df[col]))
save_issues(df[proc_bad].copy(), "processing_time_negative.csv",
            "Negative or Non-finite Processing Times")


# ── 5. FAMILY TYPE RANGE ──────────────────────────────────────────────────────
log.info("\n--- [8] Family_type Range [1, 40] ---")
fam_bad = df[~df["Family_type"].between(1, 40)].copy()
save_issues(fam_bad, "family_type_out_of_range.csv",
            "Family_type Outside [1, 40]")


# ── 6. PRIORITY ────────────────────────────────────────────────────────────────
log.info("\n--- [9] Priority (non-negative) ---")
priority_bad = df[(df["Priority"] < 0) | (~np.isfinite(df["Priority"]))].copy()
save_issues(priority_bad, "priority_invalid.csv",
            "Invalid Priority Values")


# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
log.info("\n" + "=" * 65)
log.info("VALIDATION COMPLETE")
log.info("Summary log  : %s", LOG_FILE)
log.info("Issue CSVs   : %s/", LOG_DIR)

# Count how many CSVs were created (i.e., had issues)
csv_files  = [f for f in os.listdir(LOG_DIR) if f.endswith(".csv")]
total_rows = sum(len(pd.read_csv(os.path.join(LOG_DIR, f))) for f in csv_files)
log.info("Issue files  : %d  |  Total flagged records: %d", len(csv_files), total_rows)
if csv_files:
    log.warning("Action needed — review files in Logger/ before modelling.")
else:
    log.info("Dataset is clean — safe to proceed to modelling.")
log.info("=" * 65)
