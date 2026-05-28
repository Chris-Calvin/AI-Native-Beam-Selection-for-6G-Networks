@echo off
REM ============================================================================
REM Sionna-Transfer: Main Pipeline Execution Script
REM ============================================================================

echo.
echo ============================================================================
echo SIONNA-TRANSFER: BEAM PREDICTION PIPELINE
echo ============================================================================
echo.

cd /d %~dp0

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables for optimization
set OMP_NUM_THREADS=4
set MKL_NUM_THREADS=4
set OPENBLAS_NUM_THREADS=4

echo.
echo Environment Variables:
echo  - OMP_NUM_THREADS: %OMP_NUM_THREADS%
echo  - Device: CPU (Intel i5 + Iris Xe)
echo.

REM Run main pipeline
python main.py

REM Check for errors
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Pipeline execution failed
    echo Exit code: %errorlevel%
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo PIPELINE EXECUTION COMPLETE
echo ============================================================================
echo.
echo Results saved to: .\outputs\
echo Models saved to: .\models\
echo.
pause
