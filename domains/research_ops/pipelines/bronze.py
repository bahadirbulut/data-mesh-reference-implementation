"""Research Operations Domain - Bronze Layer Pipeline

This script ingests raw experiment data from CSV files and loads it into the Bronze layer.
The Bronze layer stores data as-is from the source with minimal transformations.

Author: Research Operations Team
Domain: Research Operations
Layer: Bronze (Raw Ingestion)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, to_date

# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

# Configuration - Define source and target paths
# Source: Landing zone where experiment system drops CSV files
# Target: Bronze layer for raw data storage
source_path = "abfss://landing@<storage>.dfs.core.windows.net/research_ops/experiments/"
bronze_path = "abfss://bronze@<storage>.dfs.core.windows.net/research_ops/experiments/"

# Read raw CSV files from landing zone
# - header=true: First row contains column names
# - inferSchema=true: Automatically detect column data types
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(source_path)

# Add metadata columns for tracking and auditing
# - _ingestion_timestamp: When the data was loaded into Bronze
# - _source_file: Which file this row came from
# - _ingestion_date: Date of ingestion (used for partitioning)
df_bronze = df \
    .withColumn("_ingestion_timestamp", current_timestamp()) \
    .withColumn("_source_file", input_file_name()) \
    .withColumn("_ingestion_date", to_date(current_timestamp()))

# Write to Bronze layer using Delta Lake format
# - mode=append: Add new data without deleting existing data
# - format=delta: Use Delta Lake for ACID transactions and time travel
# - partitionBy: Partition by ingestion date for better query performance
df_bronze.write \
    .mode("append") \
    .format("delta") \
    .partitionBy("_ingestion_date") \
    .save(bronze_path)

# Log completion message with row count
print(f"Bronze load complete: {df_bronze.count()} rows ingested")
