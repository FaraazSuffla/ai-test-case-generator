#!/usr/bin/env python3
"""Cross-platform runner for AI Test Case Generator.

Automatically activates the virtual environment and delegates to
generate_tests.py — works on Windows CMD, PowerShell, Git Bash,
macOS, and Linux.

Usage:
    python testgen.py --url https://example.com/login --format playwright
    python testgen.py --demo --describe "login page" --format gherkin
    python testgen.py --costs
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VENV = ROOT / ".venv"

if sys.platform == "win32":
    VENV_PYTHON = VENV / "Scripts" / "python.exe"
else:
    VENV_PYTHON = VENV / "bin" / "python"


def main():
    if not VENV.exists() or not VENV_PYTHON.exists():
        print("[ERROR] Virtual environment not found.")
        print("        Run setup first:  python setup.py")
        sys.exit(1)

    # Re-exec generate_tests.py inside the venv, forwarding all CLI args
    cmd = [str(VENV_PYTHON), str(ROOT / "generate_tests.py")] + sys.argv[1:]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
