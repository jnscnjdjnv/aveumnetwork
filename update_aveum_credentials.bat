@echo off
echo Aveum Credentials Update Tool
echo ===========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found.
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

REM Run the update script
echo.
echo Running Aveum Credentials Update Tool...
python update_aveum_credentials.py

REM Deactivate virtual environment
call venv\Scripts\deactivate

echo.
pause 