#!/usr/bin/env python3
"""Cross-platform setup script for AI Test Case Generator.

Works on Windows (CMD, PowerShell, Git Bash), macOS, and Linux.
Run with:  python setup.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VENV = ROOT / ".venv"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
REQUIREMENTS = ROOT / "requirements.txt"

# Python executable inside the venv
if sys.platform == "win32":
    VENV_PYTHON = VENV / "Scripts" / "python.exe"
    VENV_PIP    = VENV / "Scripts" / "pip.exe"
    VENV_PW     = VENV / "Scripts" / "playwright.exe"
else:
    VENV_PYTHON = VENV / "bin" / "python"
    VENV_PIP    = VENV / "bin" / "pip"
    VENV_PW     = VENV / "bin" / "playwright"


def run(cmd, **kwargs):
    """Run a command, streaming output to the terminal."""
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"\n[ERROR] Command failed: {' '.join(str(c) for c in cmd)}")
        sys.exit(result.returncode)


def section(msg):
    print(f"\n  [..] {msg}")


def ok(msg):
    print(f"  [OK] {msg}")


def banner(msg):
    width = 46
    print("\n" + "=" * width)
    print(f"  {msg}")
    print("=" * width)


def main():
    banner("AI Test Case Generator - Setup")

    # 1. Python version check
    major, minor = sys.version_info[:2]
    if major < 3 or minor < 10:
        print(f"\n[ERROR] Python 3.10+ required (you have {major}.{minor}).")
        print("Download from https://www.python.org/downloads/")
        sys.exit(1)
    ok(f"Python {major}.{minor} found")

    # 2. Create virtual environment
    if not VENV.exists():
        section("Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(VENV)])
        ok("Virtual environment created")
    else:
        ok("Virtual environment already exists")

    # 3. Upgrade pip
    section("Upgrading pip...")
    run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    ok("pip up to date")

    # 4. Install dependencies
    section("Installing dependencies...")
    run([str(VENV_PIP), "install", "-r", str(REQUIREMENTS), "--quiet"])
    ok("Dependencies installed")

    # 5. Install Playwright browser
    section("Installing Playwright browser (chromium)...")
    run([str(VENV_PW), "install", "chromium"])
    ok("Playwright ready")

    # 6. Create .env from example
    if not ENV_FILE.exists():
        shutil.copy(ENV_EXAMPLE, ENV_FILE)
        ok(".env file created")
        api_key_needed = True
    else:
        ok(".env already exists")
        api_key_needed = False

    # 7. Done!
    banner("Setup complete!")

    if api_key_needed:
        print("""
  ACTION REQUIRED — add your API key to .env:
  --------------------------------------------
  Open .env and set:
    ANTHROPIC_API_KEY=your-key-here

  Get a free key at: https://console.anthropic.com
  --------------------------------------------
""")

    print("  DEMO (no API key needed):")
    print("    python testgen.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright")
    print()
    print("  FULL mode (after adding API key):")
    print("    python testgen.py --url https://your-app.com/login --format playwright")
    print()


if __name__ == "__main__":
    main()
