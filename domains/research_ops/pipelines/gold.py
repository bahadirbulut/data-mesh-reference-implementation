"""Research Operations Domain - Gold Layer Pipeline

This script creates the research_experiments_daily data product.
The Gold layer applies business logic and aggregates data for consumption.

Data Product: research_experiments_daily
Purpose: Daily experiment metrics including success rates and trial counts
Consumers: Research team, Data Science team, Management dashboards

Author: Research Operations Team
Domain: Research Operations
Layer: Gold (Business-Ready Data Product)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, avg, when

# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

# Configuration - Define input and output paths
# Input: Silver layer (cleaned experiments)
# Output: Gold layer (daily aggregated data product)
silver_path = "abfss://silver@<storage>.dfs.core.windows.net/research_ops/experiments/"
gold_path = "abfss://gold@<storage>.dfs.core.windows.net/research_ops/research_experiments_daily/"

# Read cleaned data from Silver layer
df_silver = spark.read.format("delta").load(silver_path)

# Business logic: Calculate daily experiment metrics
# Step 1: Group by experiment_date
# Step 2: Calculate total trials (sum of all trial counts)
# Step 3: Calculate successful trials (sum trial_count where success=true)
# Step 4: Calculate average duration
df_gold = df_silver \
    .groupBy("experiment_date") \
    .agg(
        _sum("trial_count").alias("total_trials"),  # Total number of trials per day
        _sum(when(col("success") == True, col("trial_count")).otherwise(0)).alias("successful_trials"),  # Count only successful trials
        avg("duration_minutes").alias("avg_duration_minutes")  # Average experiment duration
    ) \
    .withColumn(
        "success_rate",  # Calculate success rate as successful/total
        col("successful_trials") / col("total_trials")
    )

# Schema enforcement - Match contract exactly (experiments_v1.schema.json)
# Cast all columns to their contract-specified types
df_final = df_gold.select(
    col("experiment_date").cast("string"),  # Date as YYYY-MM-DD string
    col("total_trials").cast("double"),  # Total trials as number
    col("successful_trials").cast("double"),  # Successful trials as number
    col("success_rate").cast("double"),  # Success rate as decimal (0-1)
    col("avg_duration_minutes").cast("double")  # Average duration as number
)

# Quality checks matching contract requirements
# These ensure the data product meets all SLA commitments
assert df_final.filter(col("experiment_date").isNull()).count() == 0, "Null experiment_date"
assert df_final.filter(col("total_trials") <= 0).count() == 0, "total_trials must be > 0"
assert df_final.filter(col("successful_trials") < 0).count() == 0, "successful_trials must be >= 0"
assert df_final.filter(col("successful_trials") > col("total_trials")).count() == 0, "successful_trials > total_trials"
assert df_final.filter((col("success_rate") < 0) | (col("success_rate") > 1)).count() == 0, "Invalid success_rate"
assert df_final.filter(col("avg_duration_minutes") < 0).count() == 0, "avg_duration_minutes must be >= 0"

# Log success message
print(f"Quality checks passed. Rows: {df_final.count()}")

# Write Gold data product
# - mode=overwrite: Replace all data for idempotency
# - This creates the final data product consumed by downstream users
df_final.write \
    .mode("overwrite") \
    .format("delta") \
    .save(gold_path)

# Log completion message
print(f"Gold load complete: {df_final.count()} rows")
