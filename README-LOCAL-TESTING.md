# Local Testing Guide

Now that you have the conda environment installed, here's how to test the pipelines locally.

## Quick Start

### 1. Activate Environment
```bash
conda activate data-mesh-dev
```

### 2. Run Test Script
```bash
# From repository root
python test_local.py
```

This will:
- ✅ Initialize local Spark session
- ✅ Run Sales pipeline (Bronze → Silver → Gold)
- ✅ Run Research Ops pipeline (Bronze → Silver → Gold)
- ✅ Create Delta tables in `./output/`
- ✅ Display results and verification

### Expected Output
```
======================================================================
DATA MESH LOCAL TESTING
======================================================================
Initializing Spark session...
✓ Spark 3.4.1 initialized

======================================================================
SALES DOMAIN PIPELINE TEST
======================================================================

[1/3] Bronze Layer - Raw Ingestion
----------------------------------------------------------------------
Read 10 rows from CSV
✓ Wrote 10 rows to output/bronze/sales/orders

[2/3] Silver Layer - Validation & Cleaning
----------------------------------------------------------------------
✓ Validated 10 rows to output/silver/sales/orders

[3/3] Gold Layer - Business Aggregation
----------------------------------------------------------------------
✓ Aggregated 3 rows to output/gold/sales/daily_revenue

📊 Daily Revenue Report:
+----------+-------------+
|order_date|daily_revenue|
+----------+-------------+
|2025-01-01|       299.97|
|2025-01-02|       149.97|
|2025-01-03|        79.99|
+----------+-------------+
```

## What Gets Created

```
output/
├── bronze/
│   ├── sales/orders/              # Raw sales data
│   └── research_ops/experiments/  # Raw experiment data
├── silver/
│   ├── sales/orders/              # Validated sales data
│   └── research_ops/experiments/  # Validated experiment data
└── gold/
    ├── sales/daily_revenue/       # Aggregated sales metrics
    └── research_ops/daily_metrics/ # Aggregated experiment metrics
```

All tables are in **Delta Lake format** with:
- ACID transactions
- Time travel capabilities
- Schema evolution
- Partitioning

## Manual Testing (Step by Step)

If you want to test individual components:

### Test Bronze Layer Only
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, to_date, lit

spark = SparkSession.builder \
    .appName("BronzeTest") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .master("local[*]") \
    .getOrCreate()

# Read CSV
df = spark.read.csv("domains/sales/sample_data/orders_2025-01-01.csv", header=True, inferSchema=True)

# Add metadata
df = df.withColumn("_ingestion_timestamp", current_timestamp()) \
       .withColumn("_source_file", lit("orders_2025-01-01.csv")) \
       .withColumn("_ingestion_date", to_date(current_timestamp()))

# Write to Delta
df.write.format("delta").mode("overwrite").save("output/test_bronze")

# Verify
result = spark.read.format("delta").load("output/test_bronze")
result.show()
print(f"Count: {result.count()}")

spark.stop()
```

### Interactive Testing with PySpark Shell
```bash
# Start PySpark with Delta Lake
pyspark --packages io.delta:delta-core_2.12:2.4.0 \
        --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
        --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"

# In PySpark shell:
>>> df = spark.read.csv("domains/sales/sample_data/orders_2025-01-01.csv", header=True)
>>> df.show()
>>> df.printSchema()
>>> df.count()
```

### Query Delta Tables
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("QueryTest") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .master("local[*]") \
    .getOrCreate()

# Query Gold layer
gold = spark.read.format("delta").load("output/gold/sales/daily_revenue")
gold.createOrReplaceTempView("sales")

# Run SQL
spark.sql("""
    SELECT 
        order_date,
        ROUND(daily_revenue, 2) as revenue
    FROM sales
    ORDER BY order_date
""").show()

spark.stop()
```

## Run Governance Checks

```bash
# Validate product.yaml files
python governance/checks/validate_products.py

# Validate JSON schemas
python governance/checks/validate_schemas.py
```

Expected output:
```
OK: product.yaml checks passed
✓ Valid schema: domains/sales/contracts/sales_orders_v1.schema.json
✓ Valid schema: domains/research_ops/contracts/experiments_v1.schema.json
```

## Inspect Output Files

### View Delta Table Files
```bash
# List Delta files (PowerShell)
Get-ChildItem -Recurse output/

# Or CMD
dir output\ /s
```

### Read Parquet Files Directly
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ParquetReader").master("local[*]").getOrCreate()

# Delta tables are stored as Parquet
df = spark.read.parquet("output/gold/sales/daily_revenue/*.parquet")
df.show()

spark.stop()
```

## Troubleshooting

### Issue: Java not found
**Error:** `JAVA_HOME is not set`

**Solution:**
```bash
# Install Java via conda
conda install openjdk=11 -c conda-forge

# Verify
java -version
```

### Issue: Delta Lake import error
**Error:** `No module named 'delta'`

**Solution:**
```bash
# Reinstall delta-spark
pip install delta-spark==2.4.0
```

### Issue: Spark won't start
**Error:** `Failed to construct spark session`

**Solution:**
```bash
# Check environment
conda activate data-mesh-dev
python -c "import pyspark; print(pyspark.__version__)"

# If fails, reinstall
conda install pyspark=3.4.1 -c conda-forge
```

### Issue: Permission denied (Windows)
**Error:** `PermissionError: [WinError 5]`

**Solution:** Run as Administrator or change output directory:
```python
# In test_local.py, change output paths to:
bronze_path = "C:/temp/output/bronze/sales/orders"
```

## Clean Up Test Data

```bash
# Remove all test output (PowerShell)
Remove-Item -Recurse -Force output

# Or CMD
rmdir /s /q output
```

## Limitations of Local Testing

### ✅ What Works Locally
- PySpark transformations
- Delta Lake read/write
- Data validation logic
- Schema enforcement
- Bronze/Silver/Gold layers
- Time travel queries
- Governance checks

### ❌ What Doesn't Work Locally
- Azure Storage (ABFSS paths)
- Databricks-specific features (dbutils, secrets)
- Distributed clusters
- Job scheduling
- Production-scale data
- Unity Catalog

## Next Steps After Local Testing

1. **✅ Verify pipeline logic** - All transformations work
2. **✅ Test with sample data** - Small CSV files
3. **➡️ Deploy to Databricks** - See [README-DATABRICKS.md](README-DATABRICKS.md)
4. **➡️ Connect to Azure Storage** - ABFSS paths
5. **➡️ Schedule jobs** - Databricks Workflows
6. **➡️ Monitor production** - Azure Monitor

## Resources

- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [Delta Lake Guide](https://docs.delta.io/latest/index.html)
- [Databricks Testing](README-DATABRICKS.md)
- [Main README](README.md)
