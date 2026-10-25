@echo off
chcp 65001 >nul
title Alex Voice Assistant (Antigravity CLI)
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [CHƯA CÀI ĐẶT]: Môi trường ảo Python chưa được thiết lập.
    echo Vui lòng chạy file install.bat trước để cài đặt tự động!
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "voice_assistant.py"
pause
