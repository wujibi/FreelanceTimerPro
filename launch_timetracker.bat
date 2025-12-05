@echo off
title Time Tracker App Launcher
echo ================================================
echo          Time Tracker App Launcher
echo ================================================
echo.

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

:: Launch the application
echo Starting Time Tracker App...
echo.
python main.py

:: Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)
