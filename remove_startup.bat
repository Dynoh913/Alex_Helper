@echo off
chcp 65001 >nul
title Hủy tự khởi động Alex cùng Windows
cd /d "%~dp0"

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET_BAT=%STARTUP_FOLDER%\AlexVoiceAssistant.bat"

if exist "%TARGET_BAT%" (
    del /f /q "%TARGET_BAT%"
    echo.
    echo ==================================================================
    echo [✓ THÀNH CÔNG]: Đã xóa file tự khởi động Alex cùng Windows!
    echo ==================================================================
) else (
    echo.
    echo [THÔNG BÁO]: Không tìm thấy file khởi động nào cần xóa.
)
echo.
pause
