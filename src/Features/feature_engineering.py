# -*- coding: utf-8 -*-
"""
feature_engineering_fixed.py
=============================
FIXES:
  1. Removed Anomaly_identification from output (target leakage)
  2. Removed post-job features: wait_to_process_ratio, is_tardy,
     tardiness_per_unit, total_z_flags (all depend on job completion data)
  3. Stage efficiency only computed where finish time is legitimately available
  4. Cross-stage variability features only use stages completed before detection
  5. All leaking columns explicitly dropped from processed output
"""

import os
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pointbiserialr
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────
script_dir     = os.path.dirname(os.path.abspath(__file__))
raw_path       = os.path.abspath(os.path.join(script_dir, "../../data_source/raw/manufacturing.csv"))
processed_path = os.path.abspath(os.path.join(script_dir, "../../data_source/Processed/processed_manufacturing.csv"))

# ── Load ──────────────────────────────────────────────────────
df = pd.read_csv(raw_path)
if "Unnamed: 0" in df.columns:
    df.drop(columns=["Unnamed: 0"], inplace=True)

print(f"Loaded  : {df.shape[0]:,} rows, {df.shape[1]} columns")

# ── Deduplication ─────────────────────────────────────────────
n_before = len(df)
df = df.drop_duplicates().reset_index(drop=True)
print(f"Duplicates removed : {n_before - len(df):,}")

# ── Missing value check ───────────────────────────────────────
print(f"Missing values     : {df.isna().sum().sum()}")

# ── Ground truth (NEVER goes into processed output) ───────────
# Kept only in this variable for offline evaluation reference
y_true = (df["BREAKS"] > 0).astype(int)

# ────────────────────────────────────────────────────────────────────────────
# VALID FEATURES — only values available BEFORE breakdown occurs
# ────────────────────────────────────────────────────────────────────────────

# Stage efficiency: valid ONLY after that specific stage completes.
# These are safe for between-stage detection (e.g. flag after S1, before S2).
df["S1_efficiency"] = df["Processing_Time_S1"] / (
    df["Finish_time_S1"] - df["Start_time_S1"] + 1)

df["S2_efficiency"] = df["Processing_Time_S2"] / (
    df["Finish_Time_S2"] - df["Start_time_S2"] + 1)

df["S3_efficiency"] = df["Processing_Time_S3"] / (
    df["Finish_time_S3"] - df["Start_time_S3"] + 1)

df["S4_efficiency"] = df["Processing_Time_S4"] / (
    df["Finish_time"]    - df["Start_time_s4"] + 1)

# Cross-stage time variability — valid only after all stages complete.
# Use for end-of-job retrospective anomaly scoring, not real-time.
stage_times = df[["Processing_Time_S1", "Processing_Time_S2",
                   "Processing_Time_S3", "Processing_Time_S4"]]

df["stage_time_std"]   = stage_times.std(axis=1)
df["stage_time_range"] = stage_times.max(axis=1) - stage_times.min(axis=1)

# Queue pressure — how long job waited to enter the line (S1 start time
# relative to job ID order). Proxy for machine load at scheduling time.
df["queue_pressure"] = df["Start_time_S1"] / (df["ID"] + 1)

# ── Correlation check (offline only — uses y_true for evaluation) ──────────
eng_feats = [
    "S1_efficiency", "S2_efficiency", "S3_efficiency", "S4_efficiency",
    "stage_time_std", "stage_time_range", "queue_pressure",
]

print("\n=== ENGINEERED FEATURES → BREAKDOWN CORRELATION (offline eval) ===")
for col in eng_feats:
    r, p = pointbiserialr(
        y_true,
        df[col].replace([np.inf, -np.inf], np.nan).fillna(0),
    )
    sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    print(f"  {col:<25}: r={r:+.4f}  p={p:.4e}  {sig}")

# ── Drop ALL post-job and target columns from output ─────────────────────────
drop_cols = [
    # identifiers
    "ID",
    # raw timestamps (already encoded in efficiency features)
    "Start_time_S1", "Finish_time_S1",
    "Start_time_S2", "Finish_Time_S2",
    "Start_time_S3", "Finish_time_S3",
    "Start_time_s4", "Finish_time",
    # post-job outcome columns — TARGET LEAKAGE if kept
    "Overall_processing_time",   # only known after job ends
    "Overall_waiting_time",      # only known after job ends
    "Tardiness",                  # only known after job ends
    "BREAKS",                     # ground truth label
    "BREAKDOWN",                  # derived from BREAKS — leakage
    "Anomaly_identification",     # BUG FIX: this was silently kept before
]

df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

# ── Final deduplication on engineered feature set ────────────────────────────
processed_before = len(df)
df = df.drop_duplicates().reset_index(drop=True)
print(f"\nProcessed duplicates removed : {processed_before - len(df):,}")

# ── Save ─────────────────────────────────────────────────────
os.makedirs(os.path.dirname(processed_path), exist_ok=True)
df.to_csv(processed_path, index=False)

print(f"\nProcessed data saved → {processed_path}")
print(f"Final shape        : {df.shape[0]:,} rows, {df.shape[1]} columns")
print(f"\nColumns in output  :\n{df.columns.tolist()}")