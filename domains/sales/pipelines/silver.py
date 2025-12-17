"""Sales Domain - Silver Layer Pipeline

This script cleans and validates sales order data from Bronze layer.
The Silver layer ensures data quality through:
- Deduplication
- Data type conversions
- Data validation (null checks, value ranges)
- Column standardization

Author: Sales Analytics Team
Domain: Sales
Layer: Silver (Cleaned & Validated)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, trim, upper

# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

# Configuration - Define input and output paths
# Input: Bronze layer (raw data)
# Output: Silver layer (cleaned data)
bronze_path = "abfss://bronze@<storage>.dfs.core.windows.net/sales/orders/"
silver_path = "abfss://silver@<storage>.dfs.core.windows.net/sales/orders/"

# Read from Bronze layer
df_bronze = spark.read.format("delta").load(bronze_path)

# Data cleaning & transformations
df_silver = df_bronze \
    .dropDuplicates(["order_id"]) \  # Remove duplicate orders based on order_id
    .withColumn("order_date", to_date(col("order_date"), "yyyy-MM-dd")) \  # Convert to proper date type
    .withColumn("product", trim(col("product"))) \  # Remove leading/trailing whitespace
    .withColumn("currency", trim(upper(col("currency")))) \  # Standardize currency codes (e.g., 'eur' -> 'EUR')
    .filter(col("order_id").isNotNull()) \  # Remove rows with missing order_id
    .filter(col("quantity") > 0) \  # Ensure quantity is positive
    .filter(col("unit_price") >= 0) \  # Ensure price is non-negative
    .select(  # Select and cast columns to ensure consistent data types
        col("order_id").cast("string"),
        col("order_date"),
        col("customer_id").cast("string"),
        col("product"),
        col("quantity").cast("integer"),
        col("unit_price").cast("double"),
        col("currency")
    )

# Quality checks - Ensure data meets our standards
# These checks will fail the pipeline if data quality issues are found
assert df_silver.filter(col("order_id").isNull()).count() == 0, "Null order_id found"
assert df_silver.filter(col("quantity") <= 0).count() == 0, "Invalid quantity found"
assert df_silver.filter(col("unit_price") < 0).count() == 0, "Negative unit_price found"
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
