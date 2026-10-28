@echo off
cd /d "%~dp0"

echo [ALEX HELPER] Dang dang ky khoi dong cung Windows...

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "BAT_FILE=%STARTUP_FOLDER%\AlexVoiceAssistant.bat"

if not exist "%STARTUP_FOLDER%" (
    echo [ERROR] Khong tim thay thu muc Startup cua Windows.
    pause
    exit /b 1
)

(
echo @echo off
echo cd /d "%~dp0"
echo if exist ".venv\Scripts\pythonw.exe" (
echo     start "" ".venv\Scripts\pythonw.exe" "voice_assistant.py"
echo ^) else (
echo     start "" /min cmd.exe /c "run.bat"
echo ^)
echo exit
) > "%BAT_FILE%"

echo [THANH CONG] Tro ly Alex da duoc dang ky tu dong chay ngam cung Windows!
echo [THONG TIN] File khoi dong: "%BAT_FILE%"
pause
exit /b 0
