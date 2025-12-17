# Contract: research_experiments_daily (v1)

## Purpose
Daily experiment metrics for research operations reporting and analytics. Tracks experiment success rates and trial counts.

## Schema
See `experiments_v1.schema.json`.

## Fields

| Field Name | Type | Description | Nullable | Example |
|------------|------|-------------|----------|---------|
| experiment_date | string | Date of experiment in YYYY-MM-DD format | No | 2025-01-01 |
| total_trials | number | Total number of trials conducted | No | 150 |
| successful_trials | number | Number of successful trials | No | 120 |
| success_rate | number | Success rate as decimal (0-1) | No | 0.80 |
| avg_duration_minutes | number | Average experiment duration in minutes | No | 45.5 |

## SLA

- **Freshness**: daily @ 02:00 (Europe/Brussels)
- **Availability**: 99.5%
- **Support**: business-hours

## Quality Rules

- No missing experiment_date
- total_trials > 0
- successful_trials >= 0
- successful_trials <= total_trials
- success_rate >= 0 and success_rate <= 1
- avg_duration_minutes >= 0

## Usage Examples

### SQL (Databricks)
```sql
SELECT 
  experiment_date,
  total_trials,
  success_rate
FROM gold.research_ops.research_experiments_daily
WHERE experiment_date >= '2025-01-01'
ORDER BY experiment_date DESC
```

### Python (PySpark)
```python
df = spark.read.format("delta").load(
    "abfss://gold@storage.dfs.core.windows.net/research_ops/research_experiments_daily/"
)

# Calculate weekly averages
weekly = df.groupBy(weekofyear("experiment_date")) \
    .agg(avg("success_rate").alias("avg_weekly_success_rate"))

weekly.show()
```

## Breaking Changes

- None (initial version)

## Deprecation Notice

- Not deprecated
