# ============================================================================
# Data Mesh Development Environment Setup (PowerShell)
# ============================================================================
# This script creates a conda environment for local development and testing
# of data mesh pipelines and governance scripts.
#
# Prerequisites:
#   - Anaconda or Miniconda installed
#   - conda command available in PATH
#
# Usage:
#   1. Open PowerShell
#   2. Navigate to this directory
#   3. Run: .\setup-environment.ps1
# ============================================================================

Write-Host ""
Write-Host "========================================"
Write-Host " Data Mesh Environment Setup"
Write-Host "========================================"
Write-Host ""

# Check if conda is available
try {
    $condaVersion = & conda --version 2>&1
    Write-Host "[INFO] Found conda: $condaVersion"
    Write-Host ""
} catch {
    Write-Host "[ERROR] conda command not found!" -ForegroundColor Red
    Write-Host "Please install Anaconda or Miniconda first."
    Write-Host "Download from: https://docs.conda.io/en/latest/miniconda.html"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if environment already exists
$envExists = & conda env list | Select-String "data-mesh-dev"
if ($envExists) {
    Write-Host "[WARNING] Environment 'data-mesh-dev' already exists!" -ForegroundColor Yellow
    Write-Host ""
    $recreate = Read-Host "Do you want to remove and recreate it? (y/N)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Write-Host "[INFO] Removing existing environment..."
        & conda env remove -n data-mesh-dev -y
        Write-Host "[INFO] Environment removed"
        Write-Host ""
    } else {
        Write-Host "[INFO] Keeping existing environment"
        Write-Host "[INFO] To activate it, run: conda activate data-mesh-dev"
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 0
    }
}

# Create the environment
Write-Host "[INFO] Creating conda environment from environment.yml..."
Write-Host "[INFO] This may take several minutes..."
Write-Host ""

& conda env create -f environment.yml

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Failed to create environment!" -ForegroundColor Red
    Write-Host "Please check the error messages above."
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "Environment 'data-mesh-dev' has been created successfully."
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Activate the environment:"
Write-Host "     conda activate data-mesh-dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Verify installation:"
Write-Host "     python --version" -ForegroundColor Cyan
Write-Host "     pyspark --version" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Run governance checks:"
Write-Host "     python governance\checks\validate_products.py" -ForegroundColor Cyan
Write-Host "     python governance\checks\validate_schemas.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Test PySpark (optional):"
Write-Host "     python -c `"from pyspark.sql import SparkSession; print('PySpark works!')`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "  5. Start Jupyter Lab (optional):"
Write-Host "     jupyter lab" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================"
Write-Host ""
Read-Host "Press Enter to exit"
