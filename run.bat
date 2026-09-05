@echo off
title SysCalculus - Autonomous Cloud & Systems Simulator Engine
color 0B

echo ===============================================================================
echo                RUNTIMEZERO (syscalculus.dev) - GHOST FOUNDER DAC
echo ===============================================================================
echo [1/3] Verifying Python runtime environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo [2/3] Checking required packages (jinja2, markdown, python-frontmatter)...
python -c "import jinja2, markdown, frontmatter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [SETUP] Installing missing packages via pip...
    pip install jinja2 markdown python-frontmatter python-dotenv google-genai
)

echo [3/3] Launching Unified Ghost Founder DAC (Server + Autonomous Agents)...
echo ===============================================================================
python main.py

pause
