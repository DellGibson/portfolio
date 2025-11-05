@echo off
REM Launcher script for Alpaca Trading Bot Desktop GUI (Windows)

echo ===============================================================
echo      Alpaca Trading Bot - Desktop GUI Launcher
echo ===============================================================
echo.

REM Check if we're in the right directory
if not exist gui_app.py (
    echo [ERROR] gui_app.py not found
    echo         Please run this script from the alpaca-trading-bot directory
    pause
    exit /b 1
)

REM Check if PyQt6 is installed
echo Checking dependencies...
python -c "from PyQt6.QtWidgets import QApplication" 2>nul

if errorlevel 1 (
    echo [ERROR] PyQt6 not installed
    echo.
    echo Installing GUI dependencies...
    pip install PyQt6 PyQt6-Charts pyqtgraph qasync

    if errorlevel 1 (
        echo [ERROR] Installation failed
        echo         Try manually: pip install PyQt6 PyQt6-Charts
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed successfully
) else (
    echo [OK] PyQt6 is installed
)

REM Check .env file
if not exist .env (
    echo [WARNING] .env file not found
    echo           Copy .env.example to .env and add your API keys
    echo.
    set /p CONTINUE="Continue anyway? (Y/N): "
    if /i not "%CONTINUE%"=="Y" exit /b 1
)

REM Launch GUI
echo.
echo Launching Desktop GUI...
echo.

python gui_app.py

echo.
echo GUI closed
pause
