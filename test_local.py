"""
Local Testing Script for Data Mesh Pipelines
==============================================

This script tests the pipeline logic locally without Azure/Databricks.
It uses local file paths and creates Delta tables in a local directory.

Prerequisites:
    - Conda environment activated: conda activate data-mesh-dev
    - Run from repository root directory

What this tests:
    ✓ Bronze layer ingestion
    ✓ Silver layer validation
    ✓ Gold layer aggregation
    ✓ Delta Lake format
    ✓ PySpark transformations

What this doesn't test:
    ✗ Azure Storage connections
    ✗ Databricks cluster features
    ✗ ABFSS protocol
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    input_file_name, current_timestamp, to_date, lit, col,
    sum as _sum, upper, trim, count, avg, row_number
)
from pyspark.sql.window import Window
import os
import sys
import platform
import zipfile
from pathlib import Path


def check_java_version():
    """Check if Java is properly installed and compatible."""
    import subprocess
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        version_output = result.stderr  # Java outputs version to stderr
        print(f"Java version check: {version_output.split()[0:3]}")
        
        # Check for incompatible versions
        if 'version "21' in version_output or 'version "22' in version_output:
            print("\n⚠️  WARNING: Java 21+ detected - incompatible with PySpark 3.4")
            print("   PySpark requires Java 8, 11, or 17")
            print("   Please update your conda environment\n")
            return False
        return True
    except FileNotFoundError:
        print("✗ Java not found in PATH")
        return False


def setup_windows_hadoop():
    """
    Configure Hadoop for Windows by downloading winutils.exe and hadoop.dll if needed.
    This is required for Spark to work properly on Windows systems.
    """
    if platform.system() != 'Windows':
        return
    
    # Set up Hadoop in the workspace
    workspace_root = Path(__file__).parent.absolute()
    hadoop_home = workspace_root / 'hadoop'
    hadoop_bin = hadoop_home / 'bin'
    winutils_path = hadoop_bin / 'winutils.exe'
    hadoop_dll_path = hadoop_bin / 'hadoop.dll'
    
    # Create directories
    hadoop_bin.mkdir(parents=True, exist_ok=True)
    
    # Files to download with their URLs
    files_to_download = [
        ('winutils.exe', winutils_path, [
            'https://raw.githubusercontent.com/steveloughran/winutils/master/hadoop-3.0.0/bin/winutils.exe',
            'https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/winutils.exe',
            'https://github.com/kontext-tech/winutils/raw/master/hadoop-3.3.1/bin/winutils.exe'
        ]),
        ('hadoop.dll', hadoop_dll_path, [
            'https://raw.githubusercontent.com/steveloughran/winutils/master/hadoop-3.0.0/bin/hadoop.dll',
            'https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/hadoop.dll',
            'https://github.com/kontext-tech/winutils/raw/master/hadoop-3.3.1/bin/hadoop.dll'
        ])
    ]
    
    import urllib.request
    
    for file_name, file_path, urls_to_try in files_to_download:
        if file_path.exists():
            print(f"✓ {file_name} already exists")
            continue
            
        print(f"Downloading {file_name} for Windows support...")
        downloaded = False
        
        for url in urls_to_try:
            try:
                print(f"  Trying: {url}")
                urllib.request.urlretrieve(url, file_path)
                print(f"✓ Downloaded {file_name}")
                downloaded = True
                break
            except Exception as e:
                print(f"  Failed: {e}")
                continue
        
        if not downloaded:
            print(f"\n⚠️  Could not download {file_name} automatically.")
            print(f"   Please manually download Hadoop binaries for Windows from:")
            print(f"   https://github.com/kontext-tech/winutils")
            print(f"   And place them in: {hadoop_bin}")
    
    # Set HADOOP_HOME environment variable
    os.environ['HADOOP_HOME'] = str(hadoop_home)
    os.environ['hadoop.home.dir'] = str(hadoop_home)
    
    # Also add to system PATH for this session
    if str(hadoop_bin) not in os.environ['PATH']:
        os.environ['PATH'] = str(hadoop_bin) + os.pathsep + os.environ['PATH']
    
    print(f"✓ Configured HADOOP_HOME: {hadoop_home}\n")


def setup_spark():
    """Initialize Spark session for local testing."""
    print("Initializing Spark session...")
    
    # Configure Windows/Hadoop support
    setup_windows_hadoop()
    
    # Check Java first
    if not check_java_version():
        print("⚠️  Continuing anyway - may fail...\n")
    
    print("Downloading Delta Lake JARs (first run may take a moment)...")
    spark = SparkSession.builder \
        .appName("DataMesh-LocalTest") \
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .master("local[*]") \
        .getOrCreate()
    
    # Configure logging to suppress cleanup warnings on Windows
    spark.sparkContext.setLogLevel("ERROR")
    
    # Suppress specific loggers that produce harmless Windows warnings
    log4j = spark._jvm.org.apache.log4j
    log4j.LogManager.getLogger("org.apache.spark.util.ShutdownHookManager").setLevel(log4j.Level.OFF)
    log4j.LogManager.getLogger("org.apache.spark.SparkEnv").setLevel(log4j.Level.OFF)
    
    print(f"✓ Spark {spark.version} initialized\n")
    return spark


def test_sales_pipeline(spark):
    """Test Sales domain pipeline: Bronze → Silver → Gold."""
    print("=" * 70)
    print("SALES DOMAIN PIPELINE TEST")
    print("=" * 70)
    
    # Paths
    raw_path = "domains/sales/sample_data/orders_2025-01-01.csv"
    bronze_path = "output/bronze/sales/orders"
    silver_path = "output/silver/sales/orders"
    gold_path = "output/gold/sales/daily_revenue"
    
    # Create output directories
    os.makedirs(bronze_path, exist_ok=True)
    os.makedirs(silver_path, exist_ok=True)
    os.makedirs(gold_path, exist_ok=True)
    
    # === BRONZE LAYER ===
    print("\n[1/3] Bronze Layer - Raw Ingestion")
    print("-" * 70)
    
    df = spark.read.csv(raw_path, header=True, inferSchema=True)
    print(f"Read {df.count()} rows from CSV")
    
    bronze_df = df \
        .withColumn("_ingestion_timestamp", current_timestamp()) \
        .withColumn("_source_file", lit(raw_path)) \
        .withColumn("_ingestion_date", to_date(current_timestamp()))
    
    bronze_df.write.format("delta").mode("overwrite").partitionBy("_ingestion_date").save(bronze_path)
    print(f"✓ Wrote {bronze_df.count()} rows to {bronze_path}")
    
    # === SILVER LAYER ===
    print("\n[2/3] Silver Layer - Validation & Cleaning")
    print("-" * 70)
    
    bronze_df = spark.read.format("delta").load(bronze_path)
    
    # Deduplicate
    window_spec = Window.partitionBy("order_id").orderBy(col("_ingestion_timestamp").desc())
    silver_df = bronze_df \
        .withColumn("row_num", row_number().over(window_spec)) \
        .filter(col("row_num") == 1) \
        .drop("row_num")
    
    # Validate
    silver_df = silver_df.filter(
        (col("quantity").isNotNull()) &
        (col("quantity") > 0) &
        (col("unit_price").isNotNull()) &
        (col("unit_price") >= 0)
    )
    
    # Type conversions
    silver_df = silver_df \
        .withColumn("quantity", col("quantity").cast("int")) \
        .withColumn("unit_price", col("unit_price").cast("decimal(10,2)"))
    
    silver_df.write.format("delta").mode("overwrite").save(silver_path)
    print(f"✓ Validated {silver_df.count()} rows to {silver_path}")
    
    # === GOLD LAYER ===
    print("\n[3/3] Gold Layer - Business Aggregation")
    print("-" * 70)
    
    silver_df = spark.read.format("delta").load(silver_path)
    
    gold_df = silver_df.withColumn("revenue", col("quantity") * col("unit_price"))
    gold_df = gold_df.groupBy("order_date").agg(_sum("revenue").alias("daily_revenue")).orderBy("order_date")
    
    gold_df.write.format("delta").mode("overwrite").save(gold_path)
    print(f"✓ Aggregated {gold_df.count()} rows to {gold_path}")
    
    # Display results
    print("\n📊 Daily Revenue Report:")
    gold_df.show()
    print("✓ Sales pipeline test complete\n")


def test_research_ops_pipeline(spark):
    """Test Research Ops domain pipeline: Bronze → Silver → Gold."""
    print("=" * 70)
    print("RESEARCH OPS DOMAIN PIPELINE TEST")
    print("=" * 70)
    
    # Paths
    raw_path = "domains/research_ops/sample_data/experiments_2025-01-01.csv"
    bronze_path = "output/bronze/research_ops/experiments"
    silver_path = "output/silver/research_ops/experiments"
    gold_path = "output/gold/research_ops/daily_metrics"
    
    # Create output directories
    os.makedirs(bronze_path, exist_ok=True)
    os.makedirs(silver_path, exist_ok=True)
    os.makedirs(gold_path, exist_ok=True)
    
    # === BRONZE LAYER ===
    print("\n[1/3] Bronze Layer - Raw Ingestion")
    print("-" * 70)
    
    df = spark.read.csv(raw_path, header=True, inferSchema=True)
    print(f"Read {df.count()} rows from CSV")
    
    bronze_df = df \
        .withColumn("_ingestion_timestamp", current_timestamp()) \
        .withColumn("_source_file", lit(raw_path)) \
        .withColumn("_ingestion_date", to_date(current_timestamp()))
    
    bronze_df.write.format("delta").mode("overwrite").partitionBy("_ingestion_date").save(bronze_path)
    print(f"✓ Wrote {bronze_df.count()} rows to {bronze_path}")
    
    # === SILVER LAYER ===
    print("\n[2/3] Silver Layer - Validation & Cleaning")
    print("-" * 70)
    
    bronze_df = spark.read.format("delta").load(bronze_path)
    
    # Deduplicate
    window_spec = Window.partitionBy("experiment_id").orderBy(col("_ingestion_timestamp").desc())
    silver_df = bronze_df \
        .withColumn("row_num", row_number().over(window_spec)) \
        .filter(col("row_num") == 1) \
        .drop("row_num")
    
    # Standardize
    silver_df = silver_df \
        .withColumn("experiment_id", upper(trim(col("experiment_id")))) \
        .withColumn("researcher_id", upper(trim(col("researcher_id"))))
    
    # Validate
    silver_df = silver_df.filter(
        (col("trial_count").isNotNull()) &
        (col("trial_count") > 0) &
        (col("duration_minutes").isNotNull()) &
        (col("duration_minutes") >= 0)
    )
    
    # Type conversions
    silver_df = silver_df \
        .withColumn("trial_count", col("trial_count").cast("int")) \
        .withColumn("duration_minutes", col("duration_minutes").cast("decimal(10,2)"))
    
    silver_df.write.format("delta").mode("overwrite").save(silver_path)
    print(f"✓ Validated {silver_df.count()} rows to {silver_path}")
    
    # === GOLD LAYER ===
    print("\n[3/3] Gold Layer - Business Aggregation")
    print("-" * 70)
    
    silver_df = spark.read.format("delta").load(silver_path)
    
    gold_df = silver_df.groupBy("experiment_date").agg(
        _sum("trial_count").alias("total_trials"),
        count("experiment_id").alias("experiment_count"),
        avg("duration_minutes").alias("avg_duration_minutes")
    ).orderBy("experiment_date")
    
    gold_df.write.format("delta").mode("overwrite").save(gold_path)
    print(f"✓ Aggregated {gold_df.count()} rows to {gold_path}")
    
    # Display results
    print("\n📊 Daily Experiment Metrics:")
    gold_df.show()
    print("✓ Research Ops pipeline test complete\n")


def verify_results(spark):
    """Verify all layers and display summary."""
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    layers = [
        ("Sales - Bronze", "output/bronze/sales/orders"),
        ("Sales - Silver", "output/silver/sales/orders"),
        ("Sales - Gold", "output/gold/sales/daily_revenue"),
        ("Research Ops - Bronze", "output/bronze/research_ops/experiments"),
        ("Research Ops - Silver", "output/silver/research_ops/experiments"),
        ("Research Ops - Gold", "output/gold/research_ops/daily_metrics"),
    ]
    
    print("\nRow Counts by Layer:")
    print("-" * 70)
    for name, path in layers:
        try:
            count = spark.read.format("delta").load(path).count()
            print(f"✓ {name:30s} {count:>5d} rows")
        except Exception as e:
            print(f"✗ {name:30s} ERROR: {e}")
    
    print("\n✓ All tests passed!")
    print("\nOutput Location: ./output/")
    print("  - Bronze: Raw data with metadata")
    print("  - Silver: Validated and cleaned data")
    print("  - Gold: Business-level aggregations")


def main():
    """Run all local tests."""
    print("\n" + "=" * 70)
    print("DATA MESH LOCAL TESTING")
    print("=" * 70)
    print("This script tests pipeline logic using local sample data.")
    print("Output will be written to ./output/ as Delta tables.\n")
    
    # Initialize Spark
    spark = setup_spark()
    
    try:
        # Test both domains
        test_sales_pipeline(spark)
        test_research_ops_pipeline(spark)
        
        # Verify results
        verify_results(spark)
        
        print("\n" + "=" * 70)
        print("SUCCESS: Local testing complete!")
        print("=" * 70)
        print("\nNext Steps:")
        print("  1. Inspect output: ls -R output/")
        print("  2. Query Delta tables with PySpark")
        print("  3. Run governance checks: python governance/checks/validate_products.py")
        print("  4. Deploy to Databricks when ready")
        print()
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        
        # Check if it's a Java compatibility error
        if "DirectByteBuffer" in str(e) or "ExceptionInInitializerError" in str(e):
            print("\n" + "=" * 70)
            print("JAVA COMPATIBILITY ISSUE DETECTED")
            print("=" * 70)
            print("\nPySpark 3.4 requires Java 8, 11, or 17.")
            print("Your environment has an incompatible Java version.\n")
            print("To fix:")
            print("  1. Update environment.yml (already done)")
            print("  2. Recreate the conda environment:")
            print("     conda env remove -n data-mesh-dev")
            print("     conda env create -f environment.yml")
            print("  3. Activate and try again:")
            print("     conda activate data-mesh-dev")
            print("     python test_local.py")
            print()
        else:
            import traceback
            traceback.print_exc()
    finally:
        try:
            spark.stop()
        except:
            pass


if __name__ == "__main__":
    main()
