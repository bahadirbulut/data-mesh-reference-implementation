"""Sales Domain - Gold Layer Pipeline

This script creates the sales_orders_daily data product.
The Gold layer applies business logic and aggregates data for consumption.

Data Product: sales_orders_daily
Purpose: Daily revenue aggregates for reporting and analytics
Consumers: Finance team, Sales leadership, BI dashboards

Author: Sales Analytics Team
Domain: Sales
Layer: Gold (Business-Ready Data Product)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum

# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

# Configuration - Define input and output paths
# Input: Silver layer (cleaned orders)
# Output: Gold layer (daily aggregated data product)
silver_path = "abfss://silver@<storage>.dfs.core.windows.net/sales/orders/"
gold_path   = "abfss://gold@<storage>.dfs.core.windows.net/sales/sales_orders_daily/"

# Read cleaned data from Silver layer
df = spark.read.format("delta").load(silver_path)

# Business logic: Calculate daily revenue
# Step 1: Calculate revenue for each order (quantity * unit_price)
# Step 2: Group by order_date to get daily totals
# Step 3: Sum revenue per day
gold = (
    df.withColumn("revenue", col("quantity") * col("unit_price"))  # Calculate line-level revenue
      .groupBy("order_date")  # Group by date
      .agg(_sum("revenue").alias("daily_revenue"))  # Sum all revenue for each day
)

# Write Gold data product
# - mode=overwrite: Replace all data for idempotency
# - This creates the final data product consumed by downstream users
gold.write.mode("overwrite").format("delta").save(gold_path)
