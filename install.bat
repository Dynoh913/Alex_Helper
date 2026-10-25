@echo off
setlocal
cd /d "%~dp0"

echo ==================================================================
echo       DANG CAI DAT TRO LY AO ALEX (ANTIGRAVITY CLI)
echo ==================================================================
echo.

REM 1. Kiem tra Python
python --version >nul 2>&1
if %errorlevel% equ 0 goto :python_found

echo [ERROR]: May tinh cua ban chua cai dat Python hoac chua them vao PATH!
echo Vui long cai dat Python 3.10+ tu https://www.python.org/
echo (Luu y: Tich chon 'Add Python to PATH' khi cai dat).
echo.
pause
exit /b 1

:python_found

REM 2. Tao moi truong ao .venv
if exist ".venv\Scripts\python.exe" goto :venv_ready

echo [*] Dang tao moi truong ao Python (.venv)...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR]: Khong the tao moi truong ao .venv.
    pause
    exit /b 1
)

:venv_ready

REM 3. Cai dat thu vien
echo [*] Dang cai dat cac thu vien can thiet tu requirements.txt...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\pip.exe" install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR]: Cai dat thu vien that bai.
    pause
    exit /b 1
)

REM 4. Tai mo hinh ONNX
echo [*] Dang tai cac tep mo hinh am hoc ONNX (openWakeWord)...
".venv\Scripts\python.exe" download_models.py

REM 5. Hoi dang ky khoi dong cung Windows
echo.
echo ==================================================================
echo Ban co muon Alex tu dong chay ngam moi khi khoi dong Windows khong?
set /p startup_choice="Nhap Y (Co) hoac N (Khong) [Mac dinh: Y]: "
if /i "%startup_choice%"=="n" goto :skip_startup

call setup_startup.bat

:skip_startup
echo.
echo ==================================================================
echo [OK]: Cai dat hoan tat!
echo Ban co the nhap dup vao 'run.bat' de bat dau su dung Alex ngay.
echo ==================================================================
echo.
pause
