#!/bin/bash
# Launcher script for Alpaca Trading Bot Desktop GUI

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Alpaca Trading Bot - Desktop GUI Launcher                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "gui_app.py" ]; then
    echo "❌ Error: gui_app.py not found"
    echo "   Please run this script from the alpaca-trading-bot directory"
    exit 1
fi

# Check if PyQt6 is installed
echo "🔍 Checking dependencies..."
python -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ PyQt6 not installed"
    echo ""
    echo "📦 Installing GUI dependencies..."
    pip install PyQt6 PyQt6-Charts pyqtgraph qasync

    if [ $? -ne 0 ]; then
        echo "❌ Installation failed"
        echo "   Try manually: pip install PyQt6 PyQt6-Charts"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ PyQt6 is installed"
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and add your API keys"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Launch GUI
echo ""
echo "🚀 Launching Desktop GUI..."
echo ""

python gui_app.py

echo ""
echo "👋 GUI closed"
