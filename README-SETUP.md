# Local Development Setup Guide

This guide helps you set up a local development environment to run and test the data mesh pipelines.

## Prerequisites

- **Anaconda** or **Miniconda** installed
  - Download: https://docs.conda.io/en/latest/miniconda.html
- **Git** (for cloning the repository)
- **Windows, macOS, or Linux**

## Quick Setup

### Windows Users

#### Option 1: Command Prompt (CMD)
```cmd
setup-environment.bat
```

#### Option 2: PowerShell
```powershell
.\setup-environment.ps1
```

### macOS/Linux Users
```bash
# Create environment
conda env create -f environment.yml

# Activate environment
conda activate data-mesh-dev
```

## What Gets Installed

The conda environment includes:

| Package | Version | Purpose |
|---------|---------|---------|
| **Python** | 3.10 | Base language |
| **PySpark** | 3.4.1 | Run pipelines locally |
| **Delta-Spark** | 2.4.0 | Delta Lake support |
| **Pandas** | 2.0.3 | Data manipulation |
| **PyYAML** | 6.0 | Parse product.yaml files |
| **JSONSchema** | 4.19.0 | Validate schemas |
| **Flake8** | 6.1.0 | Code linting |
| **Black** | 23.7.0 | Code formatting |
| **Pytest** | 7.4.0 | Testing framework |
| **JupyterLab** | 4.0.5 | Interactive development |

## Verification Steps

### 1. Activate the Environment
```bash
conda activate data-mesh-dev
```

### 2. Check Python Version
```bash
python --version
# Expected: Python 3.10.x
```

### 3. Check PySpark
```bash
python -c "from pyspark.sql import SparkSession; print('PySpark works!')"
# Expected: PySpark works!
```

### 4. Run Governance Checks
```bash
python governance/checks/validate_products.py
python governance/checks/validate_schemas.py
# Expected: OK messages
```

### 5. Test Pipeline Logic (Optional)
```bash
# Create a test script
python -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('test').getOrCreate()
df = spark.read.csv('domains/sales/sample_data/orders_2025-01-01.csv', header=True)
print(f'Read {df.count()} rows')
spark.stop()
"
```

## What You Can Do Locally

### ✅ Supported Operations

1. **Run governance validation scripts**
   ```bash
   python governance/checks/validate_products.py
   python governance/checks/validate_schemas.py
   ```

2. **Test PySpark transformations**
   - Modify pipeline code
   - Test with sample CSV files
   - Validate logic before deploying

3. **Develop new data products**
   - Create new domain folders
   - Write product.yaml
   - Define schemas
   - Write pipeline code

4. **Run unit tests**
   ```bash
   pytest tests/
   ```

5. **Interactive exploration with Jupyter**
   ```bash
   jupyter lab
   # Open notebooks in browser
   ```

6. **Code quality checks**
   ```bash
   # Lint code
   flake8 domains/*/pipelines/*.py
   
   # Format code
   black domains/*/pipelines/*.py
   ```

### ❌ Limitations (Not Available Locally)

1. **Cannot connect to Azure Storage**
   - Paths like `abfss://bronze@storage...` won't work
   - Use local file paths for testing

2. **Cannot run Databricks Jobs**
   - No job scheduling
   - No cluster management

3. **Cannot access production data**
   - Use sample data only

4. **Cannot deploy pipelines**
   - Deployment requires Azure infrastructure

## Testing Pipeline Code Locally

### Modify Paths for Local Testing

**Original (Azure):**
```python
bronze_path = "abfss://bronze@<storage>.dfs.core.windows.net/sales/orders/"
```

**Modified (Local):**
```python
bronze_path = "./output/bronze/sales/orders/"
```

### Example: Test Bronze Pipeline

```bash
# Create output directory
mkdir -p output/bronze/sales/orders

# Modify domains/sales/pipelines/bronze.py temporarily
# Change paths to local paths

# Run it
python domains/sales/pipelines/bronze.py
```

## Troubleshooting

### Issue: "conda: command not found"
**Solution:** Add conda to your PATH or restart terminal after installation

### Issue: Environment creation fails
**Solution:** 
```bash
# Update conda
conda update -n base -c defaults conda

# Try again
conda env create -f environment.yml
```

### Issue: Java not found (PySpark error)
**Solution:** PySpark needs Java 8 or 11
```bash
# Install Java via conda
conda install openjdk=11 -c conda-forge
```

### Issue: Permission denied on Windows
**Solution:** Run PowerShell as Administrator

## Updating the Environment

If `environment.yml` changes:

```bash
# Update existing environment
conda env update -f environment.yml --prune

# Or remove and recreate
conda env remove -n data-mesh-dev
conda env create -f environment.yml
```

## Deactivate/Remove Environment

### Deactivate
```bash
conda deactivate
```

### Remove Completely
```bash
conda env remove -n data-mesh-dev
```

## Next Steps

After setup:

1. ✅ **Explore the repository structure**
   - Read [README.md](README.md)
   - Check domain folders

2. ✅ **Run governance checks**
   - Validate products and schemas

3. ✅ **Review pipeline code**
   - Understand bronze/silver/gold logic

4. ✅ **Create a new domain** (optional)
   - Follow [CONTRIBUTING.md](CONTRIBUTING.md)

5. ✅ **For production deployment**
   - See platform repository for infrastructure
   - Configure Databricks workspace
   - Set up Azure resources

## Support

For issues:
- Check this guide
- Review [README.md](README.md)
- Check [CONTRIBUTING.md](CONTRIBUTING.md)
- Open a GitHub issue
