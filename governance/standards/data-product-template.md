# Data Product Template

## Overview
This template provides the standard structure for creating a new data product in the mesh. Copy this structure to create your domain.

## Directory Structure

```
domains/
  {domain_name}/
    ├── product.yaml              # Metadata and SLA commitments
    ├── README.md                 # Domain documentation
    ├── contracts/                # Data contracts
    │   ├── {entity}_v1.contract.md
    │   └── {entity}_v1.schema.json
    ├── pipelines/                # ETL code
    │   ├── bronze.py             # Raw ingestion
    │   ├── silver.py             # Cleaning & validation
    │   └── gold.py               # Business logic & aggregations
    ├── sample_data/              # Sample/test data
    │   └── {entity}_2025-01-01.csv
    └── tests/                    # Unit and integration tests (optional)
        ├── test_bronze.py
        ├── test_silver.py
        └── test_gold.py
```

## File Templates

### 1. product.yaml

```yaml
name: {domain}-{entity}
domain: {domain_name}
owner:
  team: {Team Name}
  email: {team-email@example.com}

description: >
  Brief description of what this data product provides and its purpose.

inputs:
  - name: {input_source_name}
    description: "Description of the input data source"

outputs:
  - name: {output_table_name}
    layer: gold
    format: delta
    description: "Description of the output dataset"
    contract: contracts/{entity}_v1.schema.json
    version: v1

sla:
  freshness: "daily HH:MM Timezone"
  availability: "99.5%"
  support_hours: "business-hours"

quality:
  expectations:
    - "{field} is unique"
    - "{field} is not null"
    - "{condition}"

privacy:
  pii: false  # or true if contains PII
  pii_fields: []  # list PII fields if applicable

platform_dependencies:
  storage: "ADLS Gen2 (bronze/silver/gold)"
  compute: "Databricks Jobs (job clusters)"
  observability: "Log Analytics + diagnostic settings"
```

### 2. README.md

```markdown
# {Domain Name} Domain

## Overview
{Brief description of the domain and its purpose in the organization}

## Data Products

### {Product Name}
- **Purpose**: {What business need does this solve?}
- **Consumers**: {Who uses this data?}
- **Refresh**: {How often is it updated?}
- **Owner**: {Team Name} ({email})

## Data Flow

```
Source System → Bronze (raw) → Silver (cleaned) → Gold (aggregated)
```

### Bronze Layer
- **Path**: `bronze/{domain}/{entity}/`
- **Format**: CSV (raw files from source)
- **Partitioning**: By ingestion date
- **Retention**: 90 days

### Silver Layer
- **Path**: `silver/{domain}/{entity}/`
- **Format**: Delta
- **Transformations**:
  - Data type conversions
  - Deduplication
  - Data quality checks
  - Column renaming (source → standard)
- **Retention**: 2 years

### Gold Layer
- **Path**: `gold/{domain}/{entity}/`
- **Format**: Delta
- **Transformations**:
  - Business logic application
  - Aggregations (daily, weekly, etc.)
  - Joining with reference data
  - Final schema enforcement
- **Retention**: Indefinite (with archival)

## Schema

See [contracts/{entity}_v1.schema.json](contracts/{entity}_v1.schema.json)

## SLA

- **Freshness**: {timing}
- **Availability**: {percentage}
- **Support**: {hours}

## Quality Checks

- {Check 1}
- {Check 2}
- {Check 3}

## Access

To request access to this data product:
1. Submit request via {process}
2. Approval from {owner team}
3. Access granted within {timeframe}

## Known Issues

- None

## Changelog

### v1 - {Date}
- Initial release
```

### 3. {entity}_v1.contract.md

```markdown
# Contract: {entity}_daily (v1)

## Purpose
{What is this data product for? Who should use it?}

## Schema
See `{entity}_v1.schema.json`.

## Fields

| Field Name | Type | Description | Nullable | Example |
|------------|------|-------------|----------|---------|
| {field_1} | {type} | {description} | {yes/no} | {example} |
| {field_2} | {type} | {description} | {yes/no} | {example} |

## SLA

- **Freshness**: {timing and timezone}
- **Availability**: {percentage}
- **Support**: {hours}

## Quality Rules

- {rule 1}
- {rule 2}
- {rule 3}

## Usage Examples

### SQL (Databricks)
```sql
SELECT 
  {field_1},
  {field_2}
FROM {catalog}.{schema}.{entity}_daily
WHERE {condition}
```

### Python (PySpark)
```python
df = spark.read.format("delta").load(
    "abfss://gold@{storage}.dfs.core.windows.net/{domain}/{entity}/"
)
df.filter({condition}).show()
```

## Breaking Changes

- None (initial version)

## Deprecation Notice

- Not deprecated
```

### 4. {entity}_v1.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "{entity}_v1",
  "description": "{Brief description}",
  "type": "object",
  "properties": {
    "{field_1}": {
      "type": "{string|number|boolean|array|object}",
      "description": "{Field description}"
    },
    "{field_2}": {
      "type": "{type}",
      "description": "{Field description}",
      "format": "{date|date-time|email|uri|etc}"
    }
  },
  "required": ["{field_1}", "{field_2}"],
  "additionalProperties": false
}
```

### 5. bronze.py

```python
# Domain: {domain}
# Layer: Bronze (raw ingestion)

from pyspark.sql import SparkSession
from datetime import datetime

spark = SparkSession.builder.getOrCreate()

# Configuration
source_path = "abfss://landing@{storage}.dfs.core.windows.net/{domain}/{entity}/"
bronze_path = "abfss://bronze@{storage}.dfs.core.windows.net/{domain}/{entity}/"

# Read raw CSV files
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(source_path)

# Add metadata columns
from pyspark.sql.functions import current_timestamp, input_file_name

df_bronze = df \
    .withColumn("_ingestion_timestamp", current_timestamp()) \
    .withColumn("_source_file", input_file_name())

# Write to bronze (append mode)
df_bronze.write \
    .mode("append") \
    .format("delta") \
    .partitionBy("_ingestion_date") \
    .save(bronze_path)

print(f"Bronze load complete: {df_bronze.count()} rows")
```

### 6. silver.py

```python
# Domain: {domain}
# Layer: Silver (cleaning & validation)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, trim

spark = SparkSession.builder.getOrCreate()

# Configuration
bronze_path = "abfss://bronze@{storage}.dfs.core.windows.net/{domain}/{entity}/"
silver_path = "abfss://silver@{storage}.dfs.core.windows.net/{domain}/{entity}/"

# Read from bronze
df_bronze = spark.read.format("delta").load(bronze_path)

# Data cleaning & transformations
df_silver = df_bronze \
    .dropDuplicates(["{unique_key}"]) \
    .withColumn("{date_field}", to_date(col("{raw_date_field}"), "yyyy-MM-dd")) \
    .withColumn("{text_field}", trim(col("{text_field}"))) \
    .filter(col("{required_field}").isNotNull()) \
    .filter(col("{numeric_field}") > 0) \
    .select(
        col("{field_1}"),
        col("{field_2}"),
        # ... select and rename columns
    )

# Quality checks
assert df_silver.filter(col("{unique_key}").isNull()).count() == 0, "Null keys found"
assert df_silver.count() > 0, "No data after cleaning"

# Write to silver (overwrite mode for idempotency)
df_silver.write \
    .mode("overwrite") \
    .format("delta") \
    .save(silver_path)

print(f"Silver load complete: {df_silver.count()} rows")
```

### 7. gold.py

```python
# Domain: {domain}
# Product: {entity}_daily (gold)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, avg

spark = SparkSession.builder.getOrCreate()

# Configuration
silver_path = "abfss://silver@{storage}.dfs.core.windows.net/{domain}/{entity}/"
gold_path = "abfss://gold@{storage}.dfs.core.windows.net/{domain}/{entity}_daily/"

# Read from silver
df_silver = spark.read.format("delta").load(silver_path)

# Business logic & aggregations
df_gold = df_silver \
    .withColumn("{calculated_field}", col("{field_a}") * col("{field_b}")) \
    .groupBy("{date_field}") \
    .agg(
        _sum("{amount_field}").alias("{total_field}"),
        count("*").alias("{count_field}"),
        avg("{metric_field}").alias("{avg_field}")
    )

# Schema enforcement (match contract)
df_final = df_gold.select(
    col("{date_field}"),
    col("{total_field}"),
    # ... select only fields in contract
)

# Quality checks
assert df_final.filter(col("{required_field}").isNull()).count() == 0
assert df_final.filter(col("{amount_field}") < 0).count() == 0

# Write to gold (overwrite mode)
df_final.write \
    .mode("overwrite") \
    .format("delta") \
    .save(gold_path)

print(f"Gold load complete: {df_final.count()} rows")
```

### 8. Sample Data

```csv
{field_1},{field_2},{field_3}
{value_1},{value_2},{value_3}
{value_1},{value_2},{value_3}
```

## Checklist for New Data Product

- [ ] Create directory structure
- [ ] Fill in product.yaml with all required fields
- [ ] Write domain README.md
- [ ] Define schema in JSON Schema format
- [ ] Document contract in markdown
- [ ] Implement bronze.py (raw ingestion)
- [ ] Implement silver.py (cleaning)
- [ ] Implement gold.py (business logic)
- [ ] Add sample data for testing
- [ ] Add governance checks to CI/CD
- [ ] Request code review from platform team
- [ ] Test end-to-end pipeline
- [ ] Update main README with new domain
- [ ] Notify potential consumers

## Getting Help

- Platform team: platform-team@example.com
- Documentation: `/governance/`
- Standards: `/governance/standards/`
- Examples: See existing domains (`/domains/sales/`, `/domains/research_ops/`)
