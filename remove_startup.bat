@echo off
chcp 65001 >nul
title Hủy tự khởi động Alex cùng Windows
cd /d "%~dp0"

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "OLD_BAT=%STARTUP_FOLDER%\AntigravityVoice.bat"
set "TARGET_BAT=%STARTUP_FOLDER%\AlexVoiceAssistant.bat"

if exist "%OLD_BAT%" del /f /q "%OLD_BAT%"
if exist "%TARGET_BAT%" del /f /q "%TARGET_BAT%"

echo.
echo ==================================================================
echo [OK] Da xoa file tu khoi dong Alex cung Windows!
echo ==================================================================
echo.
pause
