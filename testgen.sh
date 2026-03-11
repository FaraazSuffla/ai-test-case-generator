#!/usr/bin/env bash
# testgen.sh — shortcut wrapper for AI Test Case Generator (Mac/Linux)
# Activates the venv and runs generate_tests.py with all passed arguments.

if [ ! -d ".venv" ]; then
    echo " [ERROR] Virtual environment not found. Please run: bash setup.sh"
    exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python3 generate_tests.py "$@"
