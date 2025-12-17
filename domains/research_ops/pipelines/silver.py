"""Research Operations Domain - Silver Layer Pipeline

This script cleans and validates experiment data from Bronze layer.
The Silver layer ensures data quality through:
- Deduplication
- Data type conversions
- Data validation (null checks, value ranges)
- ID standardization

Author: Research Operations Team
Domain: Research Operations
Layer: Silver (Cleaned & Validated)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, trim, upper

# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

# Configuration - Define input and output paths
# Input: Bronze layer (raw experiment data)
# Output: Silver layer (cleaned data)
bronze_path = "abfss://bronze@<storage>.dfs.core.windows.net/research_ops/experiments/"
silver_path = "abfss://silver@<storage>.dfs.core.windows.net/research_ops/experiments/"

# Read from Bronze layer
df_bronze = spark.read.format("delta").load(bronze_path)

# Data cleaning & transformations
df_silver = df_bronze \
    .dropDuplicates(["experiment_id"]) \  # Remove duplicate experiments based on experiment_id
    .withColumn("experiment_date", to_date(col("experiment_date"), "yyyy-MM-dd")) \  # Convert to proper date type
    .withColumn("experiment_id", trim(upper(col("experiment_id")))) \  # Standardize experiment IDs (e.g., 'exp001' -> 'EXP001')
    .withColumn("researcher_id", trim(upper(col("researcher_id")))) \  # Standardize researcher IDs
    .filter(col("experiment_id").isNotNull()) \  # Remove rows with missing experiment_id
    .filter(col("trial_count") > 0) \  # Ensure trial count is positive
    .filter(col("duration_minutes") >= 0) \  # Ensure duration is non-negative
    .select(  # Select and cast columns to ensure consistent data types
        col("experiment_id"),
        col("experiment_date"),
        col("trial_count"),
        col("success").cast("boolean").alias("success"),  # Ensure boolean type for success flag
        col("duration_minutes").cast("double").alias("duration_minutes"),
        col("researcher_id")
    )

# Quality checks - Ensure data meets our standards
# These checks will fail the pipeline if data quality issues are found
assert df_silver.filter(col("experiment_id").isNull()).count() == 0, "Null experiment_id found"
assert df_silver.filter(col("trial_count") <= 0).count() == 0, "Invalid trial_count found"
assert df_silver.count() > 0, "No data after cleaning"

# Log success message
print(f"Quality checks passed. Rows: {df_silver.count()}")

# Write to Silver layer
# - mode=overwrite: Replace all data for idempotent operation (safe to re-run)
# - format=delta: Use Delta Lake for ACID transactions
df_silver.write \
    .mode("overwrite") \
    .format("delta") \
    .save(silver_path)

# Log completion message
print(f"Silver load complete: {df_silver.count()} rows")
