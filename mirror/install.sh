#!/usr/bin/env bash
# MIRROR — Linux Auto-Install Script
set -e

echo "🚀 Installing MIRROR..."

# Check Python version
python3 -c "import sys; assert sys.version_info >= (3, 11)" 2>/dev/null || {
    echo "❌ Python 3.11+ required"
    exit 1
}

# Install system dependencies
echo "📦 Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3-pip python3-venv chromium-browser 2>/dev/null || true

# Create virtual environment
echo "🔧 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright Chromium..."
playwright install chromium 2>/dev/null || true

# Create database
echo "🗄️  Initializing database..."
python -c "from mirror.core.memory import Memory; Memory()"

echo ""
echo "✅ MIRROR installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config/secrets.env with your API keys"
echo "  2. Activate venv: source venv/bin/activate"
echo "  3. Run: python cli.py --clone-me (optional)"
echo "  4. Start: python cli.py --start"
echo ""
echo "Happy hunting! 🎯"
