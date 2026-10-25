@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto :run_app
echo [ERROR] Python virtual environment (.venv) not found.
echo Please run install.bat first!
pause
exit /b 1

:run_app
".venv\Scripts\python.exe" "voice_assistant.py"
pause
