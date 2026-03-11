#!/usr/bin/env bash
set -e

echo
echo " ==========================================="
echo "  AI Test Case Generator - Setup"
echo " ==========================================="
echo

# Check Python
if ! command -v python3 &>/dev/null; then
    echo " [ERROR] Python 3 not found."
    echo " Install it from https://www.python.org/downloads/ or via your package manager."
    exit 1
fi

PY_VER=$(python3 --version)
echo " [OK] $PY_VER found"

# Require Python 3.10+
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo " [ERROR] Python 3.10 or higher is required (found $PY_VER)."
    echo " Install it from https://www.python.org/downloads/"
    exit 1
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo " [..] Creating virtual environment..."
    python3 -m venv .venv
    echo " [OK] Virtual environment created"
else
    echo " [OK] Virtual environment already exists"
fi

# Activate and install
echo " [..] Installing dependencies..."
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo " [OK] Dependencies installed"

# Playwright
echo " [..] Installing Playwright browser (chromium)..."
playwright install chromium
echo " [OK] Playwright ready"

# .env setup
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo " [OK] Created .env file"
    echo
    echo " ------------------------------------------"
    echo "  ACTION REQUIRED: Add your API key to .env"
    echo " ------------------------------------------"
    echo "  Open .env in a text editor and set:"
    echo "    ANTHROPIC_API_KEY=your-key-here"
    echo
    echo "  Get a key at: https://console.anthropic.com"
    echo " ------------------------------------------"
else
    echo " [OK] .env file already exists"
fi

# Make testgen executable
chmod +x testgen.sh
echo " [OK] testgen.sh is ready"

echo
echo " ==========================================="
echo "  Setup complete!"
echo " ==========================================="
echo
echo " DEMO (no API key needed):"
echo "   ./testgen.sh --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright"
echo
echo " FULL mode (requires API key in .env):"
echo "   ./testgen.sh --url https://your-app.com/login --format playwright"
echo
