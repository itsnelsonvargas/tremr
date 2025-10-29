@echo off
REM Tremr - Launcher
REM This batch file launches the earthquake monitoring system

title Tremr - Starting...

REM Get the directory where this batch file is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Launch the GUI using pythonw (no console window)
echo Launching Tremr...
start "" pythonw.exe gui.py

REM If pythonw is not available, use python
if errorlevel 1 (
    echo pythonw not found, using python instead...
    start "" python.exe gui.py
)

REM Exit the batch file
exit
