@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo.
echo  ==========================================
echo   AI Test Case Generator - Setup
echo  ==========================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo  Please install Python 3.10+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo  [OK] Python %PY_VER% found

:: Create virtual environment
if not exist .venv (
    echo  [..] Creating virtual environment...
    python -m venv .venv
    echo  [OK] Virtual environment created
) else (
    echo  [OK] Virtual environment already exists
)

:: Activate and install dependencies
echo  [..] Installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo  [OK] Dependencies installed

:: Install Playwright browsers
echo  [..] Installing Playwright browser (chromium)...
playwright install chromium
echo  [OK] Playwright ready

:: Create .env from example if it doesn't exist
if not exist .env (
    copy .env.example .env >nul
    echo  [OK] Created .env file
    echo.
    echo  ------------------------------------------
    echo   ACTION REQUIRED: Add your API key to .env
    echo  ------------------------------------------
    echo   Open .env in a text editor and set:
    echo     ANTHROPIC_API_KEY=your-key-here
    echo.
    echo   Get a key at: https://console.anthropic.com
    echo  ------------------------------------------
) else (
    echo  [OK] .env file already exists
)

:: Copy the testgen wrapper into the project root
echo  [..] Installing testgen command...
copy /Y testgen.bat testgen_run.bat >nul
echo  [OK] You can now run: testgen.bat --url https://example.com

echo.
echo  ==========================================
echo   Setup complete!
echo  ==========================================
echo.
echo  DEMO (no API key needed):
echo    testgen.bat --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright
echo.
echo  FULL mode (requires API key in .env):
echo    testgen.bat --url https://your-app.com/login --format playwright
echo.
pause
