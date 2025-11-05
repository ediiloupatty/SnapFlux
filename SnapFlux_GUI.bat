@echo off
title SnapFlux Automation v2.0 - GUI Launcher

echo.
echo ===============================================
echo     SnapFlux Automation v2.0 - GUI Launcher
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Check if main files exist
if not exist "gui\launch_gui.py" (
    echo ERROR: gui\launch_gui.py not found!
    echo Please make sure all files are in the correct directory.
    echo.
    pause
    exit /b 1
)

if not exist "gui\gui.py" (
    echo ERROR: gui\gui.py not found!
    echo Please make sure all files are in the correct directory.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting SnapFlux GUI...
echo.

REM Launch the GUI
python gui\launch_gui.py --gui

REM If there was an error, pause so user can see it
if %errorlevel% neq 0 (
    echo.
    echo An error occurred while running the application.
    echo Check the error messages above for more information.
    echo.
    pause
)

echo.
echo SnapFlux GUI closed.
pause
