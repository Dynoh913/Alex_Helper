@echo off
chcp 65001 >nul
title Kích hoạt tự khởi động Alex cùng Windows
cd /d "%~dp0"

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET_BAT=%STARTUP_FOLDER%\AlexVoiceAssistant.bat"

(
    echo @echo off
    echo if exist "%%LOCALAPPDATA%%\Microsoft\WindowsApps\wt.exe" ^(
    echo     start "" /min wt.exe --title "Alex Voice Assistant" "%~dp0run.bat"
    echo ^) else ^(
    echo     start "" /min "Alex Voice Assistant" "%~dp0run.bat"
    echo ^)
    echo exit
) > "%TARGET_BAT%"

echo.
echo ==================================================================
echo [✓ THÀNH CÔNG]: Đã tạo file khởi động Alex cùng Windows!
echo Vị trí: %TARGET_BAT%
echo Alex sẽ tự động chạy ngầm mỗi khi bạn đăng nhập Windows.
echo ==================================================================
echo.
pause
