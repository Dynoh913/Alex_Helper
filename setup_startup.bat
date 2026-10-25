@echo off
chcp 65001 >nul
title Kích hoạt tự khởi động Alex cùng Windows
cd /d "%~dp0"

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "OLD_BAT=%STARTUP_FOLDER%\AntigravityVoice.bat"
set "TARGET_BAT=%STARTUP_FOLDER%\AlexVoiceAssistant.bat"

if exist "%OLD_BAT%" del /f /q "%OLD_BAT%"

(
    echo @echo off
    echo cd /d "%~dp0"
    echo start "" /min cmd.exe /c "run.bat"
    echo exit
) > "%TARGET_BAT%"

echo.
echo ==================================================================
echo [OK] Da tao file khoi dong Alex cung Windows!
echo Vi tri: %TARGET_BAT%
echo Alex se tu dong chay ngam moi khi ban dang nhap Windows.
echo ==================================================================
echo.
pause
