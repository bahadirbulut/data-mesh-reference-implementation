# Research Operations Domain

## Overview
The Research Operations domain owns all experiment-related data products. It provides daily experiment metrics including success rates and trial counts to support research analytics, performance tracking, and operational decision-making.

## Data Products

### Research Experiments Daily
- **Purpose**: Aggregated daily experiment metrics for research operations reporting
- **Consumers**: Research team, Data Science team, Management dashboards
- **Refresh**: Daily at 02:00 Europe/Brussels timezone
- **Owner**: Research Operations Team (research-ops@example.com)

## Data Flow

```
Operational System → CSV Export → Bronze (raw) → Silver (cleaned) → Gold (aggregated)
```

### Bronze Layer
- **Path**: `bronze/research_ops/experiments/`
- **Format**: CSV (raw files from operational system)
- **Partitioning**: By ingestion date
- **Retention**: 90 days
- **Content**: Raw experiment data as received from source

### Silver Layer
- **Path**: `silver/research_ops/experiments/`
- **Format**: Delta
- **Transformations**:
  - Remove duplicate experiment_id
  - Convert date strings to proper date types
  - Clean text fields (trim whitespace)
  - Validate trial_count > 0 and duration_minutes >= 0
  - Filter out null experiment_id
  - Standardize researcher_id format
- **Retention**: 2 years

### Gold Layer
- **Path**: `gold/research_ops/research_experiments_daily/`
- **Format**: Delta
- **Transformations**:
  - Aggregate by experiment_date
  - Sum total_trials
  - Calculate successful_trials
  - Compute success_rate (successful / total)
  - Average duration_minutes
- **Retention**: Indefinite (with archival)

## Schema

See [contracts/experiments_v1.schema.json](contracts/experiments_v1.schema.json)

## SLA

- **Freshness**: daily 02:00 Europe/Brussels
- **Availability**: 99.5%
- **Support**: business-hours (Mon-Fri 9AM-5PM CET)

## Quality Checks

- `experiment_id` is unique in silver layer
- `trial_count` > 0
- `success_rate` >= 0 and <= 1
- No missing `experiment_date`
- `successful_trials` <= `total_trials`
- `avg_duration_minutes` >= 0

## Access

To request access to this data product:
1. Submit request via email to research-ops@example.com
2. Include business justification and use case
3. Approval from Research Operations team
4. Access granted within 2 business days

## Known Issues

- None

## Changelog

### v1 - 2025-01-01
- Initial release
- Daily experiment metrics aggregation
- CSV source integration
