@echo off
REM ============================================================================
REM Sionna-Transfer: Automated Setup Script for Windows
REM ============================================================================

echo.
echo ============================================================================
echo SIONNA-TRANSFER: 6G BEAM PREDICTION SETUP
echo ============================================================================
echo.

setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python found: 
python --version

REM Navigate to project directory
cd /d %~dp0

REM Create virtual environment
echo.
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ All dependencies installed

REM Create necessary directories
echo.
echo Creating project directories...
if not exist data mkdir data
if not exist data\NewYork mkdir data\NewYork
if not exist data\LosAngeles mkdir data\LosAngeles
if not exist models mkdir models
if not exist models\openvino mkdir models\openvino
if not exist outputs mkdir outputs
echo ✓ Directories created

REM Display setup complete
echo.
echo ============================================================================
echo SETUP COMPLETE
echo ============================================================================
echo.
echo Next steps:
echo 1. Place dataset zips in Downloads folder or Project Root:
echo    - city_0_newyork_3p5.zip
echo    - city_1_losangeles_3p5.zip
echo.
echo 2. Run the pipeline:
echo    python main.py
echo.
echo 3. View results in:
echo    - .\outputs\
echo.
echo ============================================================================
echo.

pause
