@echo off
:: testgen.bat — shortcut wrapper for AI Test Case Generator (Windows)
:: Activates the venv and runs generate_tests.py with all passed arguments.

if not exist .venv (
    echo  [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
py generate_tests.py %*
