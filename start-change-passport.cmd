@echo off
setlocal
where uv >nul 2>nul
if errorlevel 1 (
  echo [Change Passport] Please install uv first: https://docs.astral.sh/uv/
  pause
  exit /b 1
)
cd /d "%~dp0"
uv run change-passport start
if errorlevel 1 pause
