@echo off
REM Test runner batch script for Windows
echo File Backup System - Local Test Runner
echo =====================================

REM Change to project root directory
cd /d %~dp0..

echo.
echo Installing/updating test dependencies...
python -m pip install -r requirements-dev.txt

echo.
echo Running code quality checks...
echo.

echo [1/4] Running flake8 linting...
python -m flake8 src
if %ERRORLEVEL% neq 0 (
    echo FAILED: Code linting failed
    pause
    exit /b 1
)
echo PASSED: Code linting

echo.
echo [2/4] Checking code formatting with black...
python -m black --check src tests
if %ERRORLEVEL% neq 0 (
    echo FAILED: Code formatting check failed
    echo Run: python -m black . to fix formatting
    pause
    exit /b 1
)
echo PASSED: Code formatting

echo.
echo [3/4] Running unit tests...
setlocal
set PYTHONPATH=%CD%\src
python -m pytest tests/ -v
if %ERRORLEVEL% neq 0 (
    endlocal
    echo FAILED: Unit tests failed
    pause
    exit /b 1
)
endlocal
echo PASSED: Unit tests

echo.
echo [4/4] Testing module imports...
setlocal
set PYTHONPATH=%CD%\src
python -c "import main; print('Main module imports successfully')"
if %ERRORLEVEL% neq 0 (
    endlocal
    echo FAILED: Import test failed
    pause
    exit /b 1
)
endlocal
echo PASSED: Import test

echo.
echo ========================================
echo All checks passed! Ready to push to CI.
echo ========================================
pause
