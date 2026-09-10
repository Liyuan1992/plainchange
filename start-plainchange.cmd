@echo off
setlocal
where uv >nul 2>nul
if errorlevel 1 (
  echo [PlainChange] Please install uv first: https://docs.astral.sh/uv/
  pause
  exit /b 1
)
cd /d "%~dp0"
uv run plainchange serve
if errorlevel 1 pause
