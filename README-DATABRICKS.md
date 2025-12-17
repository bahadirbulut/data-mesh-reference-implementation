# Testing in Databricks

This guide shows how to test the data mesh pipelines in Databricks without needing full Azure infrastructure.

## Option 1: Databricks Community Edition (Free)

### What You Get
- **Free Databricks workspace**
- Single-node cluster (15GB RAM, 2 cores)
- Notebook interface
- DBFS storage (limited)
- No Azure integration needed

### Limitations
- No multi-node clusters
- Limited compute resources
- No job scheduling
- DBFS storage only (no ADLS connection)
- Session timeout after inactivity

### Setup Steps

1. **Sign up for Community Edition**
   - Go to: https://community.cloud.databricks.com/login.html
   - Click "Sign up" 
   - Use personal email (free, no credit card)

2. **Create a Cluster**
   - Click "Compute" in sidebar
   - Click "Create Cluster"
   - Name: `data-mesh-test`
   - Runtime: `13.3 LTS` (includes Spark 3.4, Delta Lake)
   - Click "Create Cluster"
   - Wait 3-5 minutes for startup

3. **Upload Sample Data**
   - Click "Data" in sidebar
   - Click "Create Table"
   - Drop files: `domains/sales/sample_data/orders_2025-01-01.csv`
   - Drop files: `domains/research_ops/sample_data/experiments_2025-01-01.csv`
   - Click "Create Table with UI" → "Upload File"
   - Note the DBFS paths (e.g., `/FileStore/tables/orders_2025_01_01.csv`)

4. **Import Setup Notebook**
   - Click "Workspace" in sidebar
   - Right-click your user folder → "Import"
   - Upload: `databricks-setup.ipynb` (see below)
   - Or drag/drop the .dbc file

5. **Run the Notebook**
   - Open `databricks-setup.ipynb`
   - Attach cluster: `data-mesh-test`
   - Run all cells (Shift+Enter)
   - Verify outputs

## Option 2: Azure Databricks Trial (14 days)

### What You Get
- Full Databricks workspace
- Multi-node clusters
- Azure Storage integration
- Job scheduling
- Production-like environment

### Setup Steps

1. **Start Free Trial**
   - Go to: https://azure.microsoft.com/free/
   - Create Azure account (requires credit card, but won't charge)
   - $200 credit for 30 days

2. **Create Databricks Workspace**
   ```bash
   # Azure Portal → Create Resource → "Azure Databricks"
   # Or use Azure CLI:
   az login
   az group create --name rg-datamesh-dev --location eastus
   az databricks workspace create \
     --resource-group rg-datamesh-dev \
     --name databricks-datamesh-dev \
     --location eastus \
     --sku trial
   ```

3. **Create ADLS Gen2 Storage (Optional)**
   ```bash
   az storage account create \
     --name stdatameshdev \
     --resource-group rg-datamesh-dev \
     --location eastus \
     --sku Standard_LRS \
     --kind StorageV2 \
     --hierarchical-namespace true
   
   # Create containers
   az storage container create --name bronze --account-name stdatameshdev
   az storage container create --name silver --account-name stdatameshdev
   az storage container create --name gold --account-name stdatameshdev
   ```

4. **Configure Service Principal (Optional)**
   ```bash
   # For ADLS authentication
   az ad sp create-for-rbac --name sp-datamesh-dev
   # Save client_id, client_secret, tenant_id
   
   # Grant permissions
   az role assignment create \
     --assignee <client_id> \
     --role "Storage Blob Data Contributor" \
     --scope /subscriptions/<sub_id>/resourceGroups/rg-datamesh-dev/providers/Microsoft.Storage/storageAccounts/stdatameshdev
   ```

5. **Import Pipelines**
   - Upload pipeline files as notebooks
   - Modify paths to use ABFSS or DBFS
   - Run with cluster

## Testing Approach

### 1. Quick Test (DBFS Paths)

Modify pipeline paths to use DBFS:

**Before (Azure ADLS):**
```python
bronze_path = "abfss://bronze@<storage>.dfs.core.windows.net/sales/orders/"
```

**After (DBFS):**
```python
bronze_path = "/dbfs/bronze/sales/orders/"
# or
bronze_path = "dbfs:/bronze/sales/orders/"
```

### 2. Full Test (With ADLS)

Keep original ABFSS paths and configure authentication:

```python
# In notebook or cluster config
spark.conf.set(
    f"fs.azure.account.auth.type.<storage>.dfs.core.windows.net",
    "OAuth"
)
spark.conf.set(
    f"fs.azure.account.oauth.provider.type.<storage>.dfs.core.windows.net",
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.id.<storage>.dfs.core.windows.net",
    "<client_id>"
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.secret.<storage>.dfs.core.windows.net",
    "<client_secret>"
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.endpoint.<storage>.dfs.core.windows.net",
    f"https://login.microsoftonline.com/<tenant_id>/oauth2/token"
)
```

## What to Test

### ✅ Bronze Layer
- Upload CSV to DBFS
- Run bronze.py
- Verify:
  - Schema inference
  - Metadata columns added
  - Partitioning by date
  - Delta format

### ✅ Silver Layer
- Run silver.py
- Verify:
  - Deduplication works
  - Data quality checks
  - Type conversions
  - Null handling

### ✅ Gold Layer
- Run gold.py
- Verify:
  - Aggregations correct
  - Business logic
  - Final schema matches contract

### ✅ Governance
- Run validation scripts
- Test schema compliance
- Check product.yaml

## Example: Test Sales Pipeline

### Step 1: Upload Data to DBFS
```python
# In Databricks notebook
dbutils.fs.cp(
    "file:/Workspace/Users/<your_email>/orders_2025-01-01.csv",
    "dbfs:/raw/sales/orders_2025-01-01.csv"
)
```

### Step 2: Run Bronze (Modified for DBFS)
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, current_timestamp, to_date

# Initialize Spark
spark = SparkSession.builder.appName("bronze_sales").getOrCreate()

# Read CSV from DBFS
raw_path = "dbfs:/raw/sales/orders_2025-01-01.csv"
bronze_path = "dbfs:/bronze/sales/orders/"

df = spark.read.csv(raw_path, header=True, inferSchema=True)

# Add metadata
df = df.withColumn("_ingestion_timestamp", current_timestamp()) \
       .withColumn("_source_file", input_file_name()) \
       .withColumn("_ingestion_date", to_date(current_timestamp()))

# Write to Delta
df.write.format("delta") \
    .mode("append") \
    .partitionBy("_ingestion_date") \
    .save(bronze_path)

print(f"✓ Bronze: Wrote {df.count()} rows")
```

### Step 3: Run Silver
```python
from pyspark.sql.functions import col

bronze_df = spark.read.format("delta").load("dbfs:/bronze/sales/orders/")

# Deduplicate
silver_df = bronze_df.dropDuplicates(["order_id"])

# Validate
silver_df = silver_df.filter(
    (col("quantity") > 0) & 
    (col("unit_price") >= 0)
)

# Type casting
silver_df = silver_df.withColumn("quantity", col("quantity").cast("int")) \
                     .withColumn("unit_price", col("unit_price").cast("decimal(10,2)"))

# Write
silver_path = "dbfs:/silver/sales/orders/"
silver_df.write.format("delta").mode("overwrite").save(silver_path)

print(f"✓ Silver: {silver_df.count()} rows validated")
```

### Step 4: Run Gold
```python
from pyspark.sql.functions import sum as _sum

silver_df = spark.read.format("delta").load("dbfs:/silver/sales/orders/")

# Calculate revenue
gold_df = silver_df.withColumn(
    "revenue",
    col("quantity") * col("unit_price")
)

# Aggregate
gold_df = gold_df.groupBy("order_date").agg(
    _sum("revenue").alias("daily_revenue")
)

# Write
gold_path = "dbfs:/gold/sales/daily_revenue/"
gold_df.write.format("delta").mode("overwrite").save(gold_path)

print(f"✓ Gold: {gold_df.count()} aggregated rows")
gold_df.show()
```

## Verifying Results

```python
# Check Delta tables
display(spark.read.format("delta").load("dbfs:/bronze/sales/orders/"))
display(spark.read.format("delta").load("dbfs:/silver/sales/orders/"))
display(spark.read.format("delta").load("dbfs:/gold/sales/daily_revenue/"))

# Check row counts
print(f"Bronze: {spark.read.format('delta').load('dbfs:/bronze/sales/orders/').count()}")
print(f"Silver: {spark.read.format('delta').load('dbfs:/silver/sales/orders/').count()}")
print(f"Gold: {spark.read.format('delta').load('dbfs:/gold/sales/daily_revenue/').count()}")

# Query gold data
spark.sql("""
SELECT * FROM delta.`dbfs:/gold/sales/daily_revenue/`
ORDER BY order_date
""").show()
```

## Cost Management

### Community Edition
- **Cost:** $0 (completely free)
- **Limit:** Single user, basic cluster

### Azure Trial
- **Free tier:** $200 credit
- **Minimize costs:**
  - Stop clusters when not in use
  - Use smallest cluster size for testing
  - Delete resources after testing
  - Set auto-termination to 30 minutes

```python
# In notebook - auto-terminate cluster
dbutils.notebook.exit("Pipeline complete - cluster will auto-terminate")
```

## Troubleshooting

### Issue: Cluster won't start
**Solution:** Community Edition has queue - wait or try off-peak hours

### Issue: "File not found" error
**Solution:** Check DBFS path syntax - use `dbfs:/` not `/dbfs/`

### Issue: Delta Lake errors
**Solution:** Ensure runtime version 11.0+ (includes Delta Lake)

### Issue: Out of memory
**Solution:** 
- Reduce data size
- Add `.limit(1000)` for testing
- Use `.sample(0.1)` to process 10% of data

## Next Steps After Testing

1. **Validate pipeline logic** ✅
2. **Test with larger datasets** 
3. **Add error handling**
4. **Create reusable functions**
5. **Set up CI/CD** (GitHub Actions)
6. **Deploy to production Azure**

## Resources

- [Databricks Community Edition](https://community.cloud.databricks.com/)
- [Azure Free Trial](https://azure.microsoft.com/free/)
- [Delta Lake Quickstart](https://docs.delta.io/latest/quick-start.html)
- [Databricks Documentation](https://docs.databricks.com/)
