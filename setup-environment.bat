@echo off
REM ============================================================================
REM Data Mesh Development Environment Setup
REM ============================================================================
REM This script creates a conda environment for local development and testing
REM of data mesh pipelines and governance scripts.
REM
REM Prerequisites:
REM   - Anaconda or Miniconda installed
REM   - conda command available in PATH
REM
REM Usage:
REM   1. Open Command Prompt or PowerShell
REM   2. Navigate to this directory
REM   3. Run: setup-environment.bat
REM ============================================================================

echo.
echo ========================================
echo  Data Mesh Environment Setup
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] conda command not found!
    echo Please install Anaconda or Miniconda first.
    echo Download from: https://docs.conda.io/en/latest/miniconda.html
    echo.
    pause
    exit /b 1
)

echo [INFO] Found conda installation
echo.

REM Check if environment already exists
conda env list | findstr "data-mesh-dev" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Environment 'data-mesh-dev' already exists!
    echo.
    set /p RECREATE="Do you want to remove and recreate it? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo [INFO] Removing existing environment...
        call conda env remove -n data-mesh-dev -y
        echo [INFO] Environment removed
        echo.
    ) else (
        echo [INFO] Keeping existing environment
        echo [INFO] To activate it, run: conda activate data-mesh-dev
        echo.
        pause
        exit /b 0
    )
)

REM Create the environment
echo [INFO] Creating conda environment from environment.yml...
echo [INFO] This may take several minutes...
echo.

call conda env create -f environment.yml

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to create environment!
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Environment 'data-mesh-dev' has been created successfully.
echo.
echo Next steps:
echo   1. Activate the environment:
echo      conda activate data-mesh-dev
echo.
echo   2. Verify installation:
echo      python --version
echo      pyspark --version
echo.
echo   3. Run governance checks:
echo      python governance\checks\validate_products.py
echo      python governance\checks\validate_schemas.py
echo.
echo   4. Test PySpark (optional):
echo      python -c "from pyspark.sql import SparkSession; print('PySpark works!')"
echo.
echo   5. Start Jupyter Lab (optional):
echo      jupyter lab
echo.
echo ========================================
echo.
pause
