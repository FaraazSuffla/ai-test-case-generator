@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo.
echo  ==========================================
echo   AI Test Case Generator - Setup
echo  ==========================================
echo.

:: Check Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo  Please install Python 3.10+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('py --version 2^>^&1') do set PY_VER=%%i
echo  [OK] Python %PY_VER% found

:: Check Python is 3.10+
for /f "tokens=1,2 delims=." %%a in ("%PY_VER%") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)
if %PY_MAJOR% LSS 3 goto :pyver_fail
if %PY_MAJOR% EQU 3 if %PY_MINOR% LSS 10 goto :pyver_fail
goto :pyver_ok
:pyver_fail
echo  [ERROR] Python 3.10+ required. Found %PY_VER%.
echo  Download: https://www.python.org/downloads/
pause
exit /b 1
:pyver_ok

:: Create virtual environment
if not exist .venv (
    echo  [..] Creating virtual environment...
    py -m venv .venv
    echo  [OK] Virtual environment created
) else (
    echo  [OK] Virtual environment already exists
)

:: Activate and install dependencies
echo  [..] Installing dependencies...
call .venv\Scripts\activate.bat
py -m pip install --upgrade pip --quiet
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

echo  [..] Verifying setup...
call testgen.bat --check

pause
