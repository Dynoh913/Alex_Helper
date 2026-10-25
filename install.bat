@echo off
chcp 65001 >nul
title Cài đặt Alex Helper - Antigravity Voice Assistant
cd /d "%~dp0"

echo ==================================================================
echo       ĐANG CÀI ĐẶT TRỢ LÝ ẢO ALEX (ANTIGRAVITY CLI)
echo ==================================================================
echo.

REM 1. Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LỖI]: Máy tính của bạn chưa cài đặt Python!
    echo Vui lòng tải và cài đặt Python 3.10+ từ https://www.python.org/
    echo (Lưu ý: Nhớ tích chọn 'Add Python to PATH' khi cài đặt).
    echo.
    pause
    exit /b 1
)

REM 2. Tạo môi trường ảo .venv
if not exist ".venv" (
    echo [*] Đang tạo môi trường ảo Python (.venv)...
    python -m venv .venv
)

REM 3. Nâng cấp pip và cài đặt thư viện
echo [*] Đang cài đặt các thư viện cần thiết từ requirements.txt...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\pip.exe" install -r requirements.txt

REM 4. Tải mô hình âm học ONNX
echo [*] Đang tải các tệp mô hình âm học ONNX (openWakeWord)...
".venv\Scripts\python.exe" download_models.py

REM 5. Hỏi người dùng có muốn đăng ký tự khởi động cùng Windows
echo.
echo ==================================================================
echo Bạn có muốn Alex tự động chạy ngầm mỗi khi khởi động máy không?
set /p startup_choice="Nhập Y (Có) hoặc N (Không) [Mặc định: Y]: "
if /i "%startup_choice%"=="n" goto skip_startup

call setup_startup.bat

:skip_startup
echo.
echo ==================================================================
echo [✓ CHÚC MỪNG]: Cài đặt hoàn tất!
echo Bạn có thể nhấp đúp vào 'run.bat' để bắt đầu sử dụng Alex ngay.
echo ==================================================================
echo.
pause
