@echo off
:: Time Tracker App - No Console Window Launcher

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x and try again
    pause
    exit /b 1
)

:: Change to script directory
cd /d "%~dp0"

:: Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found in current directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

:: Launch the application WITHOUT console window
start "" pythonw main.py

:: Exit immediately (no console window persists)
exit
