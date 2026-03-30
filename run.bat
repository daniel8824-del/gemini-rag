@echo off
cd /d "%~dp0"
uv run --with google-genai main.py
pause
