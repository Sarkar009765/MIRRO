@echo off
REM MIRROR — Windows Auto-Install Script
echo 🚀 Installing MIRROR...

REM Check Python version
python --version 2>nul | findstr /R "3\.1[1-9]" >nul
if errorlevel 1 (
    echo ❌ Python 3.11+ required
    echo Download from: https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo 🔧 Setting up virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install Python packages
echo 📦 Installing Python dependencies...
pip install -q -r requirements.txt

REM Install Playwright browsers
echo 🌐 Installing Playwright Chromium...
python -m playwright install chromium 2>nul

REM Create database
echo 🗄️  Initializing database...
python -c "from mirror.core.memory import Memory; Memory()"

echo.
echo ✅ MIRROR installation complete!
echo.
echo Next steps:
echo   1. Edit config\secrets.env with your API keys
echo   2. Activate venv: venv\Scripts\activate
echo   3. Run: python cli.py --clone-me (optional)
echo   4. Start: python cli.py --start
echo.
echo Happy hunting! 🎯
pause
