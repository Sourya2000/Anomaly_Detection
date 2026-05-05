# CI/CD Pipeline Setup Guide

## Overview

The project uses GitLab CI/CD to automate data ingestion, validation, and feature engineering. The pipeline has three stages:

1. **Ingest** - Upload raw dataset to Garage S3
2. **Validate** - Validate data quality
3. **Prepare** - Run feature engineering with DVC

## Prerequisites

- GitLab project with CI/CD enabled
- Garage S3 access (for data storage)
- Python 3.11+ runtime available in GitLab Runner

## Setup Instructions

### 1. Set AWS Credentials (GitLab UI)

These credentials are required for the `ingest_data` job to upload to Garage S3.

**Steps:**
1. Go to your GitLab project → **Settings** → **CI/CD** → **Variables**
2. Add the following **protected** and **masked** variables:
   - `AWS_ACCESS_KEY_ID` - Your Garage access key
   - `AWS_SECRET_ACCESS_KEY` - Your Garage secret key

**Why masked?** - These are sensitive credentials and should never appear in logs.

**Why protected?** - Only runs on protected branches (main, develop) by default.

### 2. Configure Garage Endpoint (Optional)

If your Garage endpoint differs from the default, update in `.gitlab-ci.yml`:

```yaml
variables:
  AWS_ENDPOINT_URL_S3: "http://your-garage-endpoint:3900"
  AWS_DEFAULT_REGION: "garage"
```

### 3. Trigger Pipeline

The pipeline automatically runs when you:
- Push to `main` branch
- Push to `develop` branch
- Create a merge request

To manually trigger:
1. Go to **CI/CD** → **Pipelines**
2. Click **Run pipeline** button

## Pipeline Jobs

### ingest_data (Ingest Stage)
- **Purpose**: Upload raw manufacturing.csv to Garage S3
- **Script**: `python src/data/ingest_data.py`
- **Artifacts**: Raw dataset (30 days retention)
- **Dependencies**: Requires `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### validate_data (Validate Stage)
- **Purpose**: Validate data quality before processing
- **Script**: `python src/data/data_validation.py`
- **Artifacts**: Validation logs in `Logger/` directory
- **Depends on**: `ingest_data` job completion

### prepare_features (Prepare Stage)
- **Purpose**: Run feature engineering pipeline with DVC
- **Script**: `dvc repro`
- **Artifacts**: Processed dataset (14,412 rows × 17 cols)
- **Depends on**: `validate_data` job completion

## Local Development vs CI/CD

### Local Development
```bash
# Run without AWS credentials - skips upload
python src/data/ingest_data.py
# Output: "[INFO] AWS credentials not found in environment. Skipping S3 upload."
```

### CI/CD Pipeline
```bash
# Runs with AWS credentials from GitLab variables
# Automatically uploads to Garage
python src/data/ingest_data.py
# Output: "Upload complete!"
```

## Troubleshooting

### Job Fails: "Missing AWS credentials"
- Check that `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set in GitLab
- Verify credentials are not expired
- Ensure job is running on a protected branch

### Job Fails: "ModuleNotFoundError: boto3"
- Check that `boto3` is in `requirements.txt` ✓ (already added)
- Verify pip install succeeds in build logs

### Job Fails: "Dataset file not found"
- Verify `data_source/raw/manufacturing.csv` exists in repository
- Check that ingest_data job artifacts are preserved

## Pipeline Flow Diagram

```
┌─────────────────────┐
│   ingest_data       │
│ (Upload raw CSV)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  validate_data      │
│ (Check quality)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ prepare_features    │
│ (DVC pipeline)      │
└─────────────────────┘
```

## Advanced Configuration

### Run Pipeline Only on Main Branch
```yaml
only:
  - main
```

### Run Pipeline on Merge Requests
```yaml
only:
  - merge_requests
```

### Schedule Daily Runs
1. Go to **CI/CD** → **Schedules**
2. Click **New schedule**
3. Set frequency and branches

### Use Custom Docker Image
```yaml
image: python:3.11-slim
```

## Next Steps

1. Commit `.gitlab-ci.yml` to repository
2. Set AWS credentials in GitLab Settings
3. Push to `main` or `develop` branch
4. Monitor pipeline in **CI/CD** → **Pipelines**
5. Check job logs for errors or warnings
