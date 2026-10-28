import os
import re
import sys
import time
import ctypes
import datetime
import subprocess
import webbrowser
import urllib.parse
import tkinter as tk
import keyboard

# -------------------------------------------------------------
# 1. HỆ THỐNG & PHẦN CỨNG WINDOWS
# -------------------------------------------------------------

def get_time_date_info():
    """Lấy ngày giờ hiện tại bằng tiếng Việt tự nhiên"""
    now = datetime.datetime.now()
    weekdays = ["thứ Hai", "thứ Ba", "thứ Tư", "thứ Năm", "thứ Sáu", "thứ Bảy", "Chủ Nhật"]
    weekday_str = weekdays[now.weekday()]
    return f"Bây giờ là {now.hour} giờ {now.minute:02d} phút, {weekday_str}, ngày {now.day} tháng {now.month} năm {now.year}."

def get_battery_info():
    """Lấy thông tin pin và trạng thái sạc qua Windows API native"""
    try:
        class SPS(ctypes.Structure):
            _fields_ = [
                ('AC', ctypes.c_byte),
                ('Flag', ctypes.c_byte),
                ('Percent', ctypes.c_byte),
                ('Status', ctypes.c_byte),
                ('LifeTime', ctypes.c_ulong),
                ('FullLifeTime', ctypes.c_ulong)
            ]
        s = SPS()
        ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))
        if s.Percent == 255:
            return "Máy tính không có pin hoặc đang dùng nguồn cố định."
        ac_str = "đang cắm sạc nguồn" if s.AC == 1 else "đang dùng pin"
        return f"Pin máy tính hiện tại còn {s.Percent}%, {ac_str}."
    except Exception as e:
        return f"Không thể kiểm tra pin lúc này."

def change_volume(action="up", steps=5):
    """Điều khiển âm lượng hệ thống Windows (up, down, mute)"""
    try:
        if action == "up":
            for _ in range(steps):
                keyboard.send("volume up")
            return "Đã tăng âm lượng."
        elif action == "down":
            for _ in range(steps):
                keyboard.send("volume down")
            return "Đã giảm âm lượng."
        elif action == "mute":
            keyboard.send("volume mute")
            return "Đã chuyển trạng thái âm thanh."
    except Exception:
        pass
    return "Không thể chỉnh âm lượng."

def change_brightness(direction="up", delta=15):
    """Điều chỉnh độ sáng màn hình trên laptop qua WMI PowerShell ngầm"""
    try:
        cmd_get = "powershell -Command \"(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness).CurrentBrightness\""
        cur = subprocess.check_output(cmd_get, shell=True, text=True, errors="ignore").strip()
        lines = [line.strip() for line in cur.splitlines() if line.strip().isdigit()]
        if not lines:
            return "Máy tính không hỗ trợ điều chỉnh độ sáng qua phần mềm."
        cur_val = int(lines[-1])
        new_val = min(100, cur_val + delta) if direction == "up" else max(10, cur_val - delta)
        
        cmd_set = f"powershell -Command \"(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(1, {new_val})\""
        subprocess.Popen(cmd_set, shell=True)
        return f"Đã chỉnh độ sáng lên {new_val}%."
    except Exception:
        return "Không thể điều chỉnh độ sáng."

def lock_computer():
    """Khóa màn hình máy tính ngay lập tức"""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Đã khóa máy tính."
    except Exception:
        return "Lỗi khi khóa máy tính."

def show_desktop():
    """Ẩn tất cả cửa sổ để hiển thị màn hình chính (Desktop)"""
    try:
        keyboard.send("win+d")
        return "Đã hiển thị màn hình Desktop."
    except Exception:
        return "Không thể thu nhỏ cửa sổ."

def take_screenshot():
    """Kích hoạt công cụ chụp ảnh màn hình Windows Snipping Tool"""
    try:
        keyboard.send("win+shift+s")
        return "Đã mở công cụ chụp ảnh màn hình."
    except Exception:
        return "Không thể kích hoạt chụp màn hình."

def close_active_window():
    """Đóng cửa sổ hoặc tab ứng dụng đang mở"""
    try:
        keyboard.send("alt+f4")
        return "Đã đóng cửa sổ hiện tại."
    except Exception:
        return "Không thể đóng cửa sổ."

# -------------------------------------------------------------
# 2. KHỞI CHẠY ỨNG DỤNG & TRANG WEB
# -------------------------------------------------------------

COMMON_WEBSITES = {
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "shopee": "https://shopee.vn",
    "zalo web": "https://chat.zalo.me",
}

COMMON_APPS = {
    "chrome": "start chrome",
    "trình duyệt": "start chrome",
    "cốc cốc": "start coccoc",
    "edge": "start msedge",
    "notepad": "start notepad",
    "ghi chú": "start notepad",
    "máy tính": "start calc",
    "calculator": "start calc",
    "thư mục": "start explorer",
    "quản lý tệp": "start explorer",
    "explorer": "start explorer",
    "word": "start winword",
    "excel": "start excel",
    "powerpoint": "start powerpnt",
    "zalo": "start zalo",
    "spotify": "start spotify",
    "vs code": "start code",
    "code": "start code",
    "task manager": "start taskmgr",
    "quản lý tác vụ": "start taskmgr",
    "cài đặt": "start ms-settings:",
    "settings": "start ms-settings:",
}

def open_web_or_app(name):
    """Mở ứng dụng hoặc trang web theo tên thường gọi"""
    name_clean = name.lower().strip()
    
    # Kiểm tra trang web
    for site_key, url in COMMON_WEBSITES.items():
        if site_key in name_clean:
            webbrowser.open(url)
            return f"Đã mở {site_key.title()} trên trình duyệt."

    # Kiểm tra ứng dụng Windows
    for app_key, cmd in COMMON_APPS.items():
        if app_key in name_clean:
            os.system(cmd)
            return f"Đã mở ứng dụng {app_key.title()}."

    # Mặc định thử start tên ứng dụng
    try:
        os.system(f"start {name_clean}")
        return f"Đang khởi động {name_clean}."
    except Exception:
        return f"Không tìm thấy ứng dụng {name_clean}."

def search_google_or_youtube(query, target="google"):
    """Tìm kiếm nội dung trên Google hoặc YouTube"""
    if not query:
        return "Bạn muốn tìm kiếm điều gì?"
    encoded = urllib.parse.quote(query)
    if "youtube" in target.lower():
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"Đang tìm kiếm {query} trên YouTube."
    else:
        url = f"https://www.google.com/search?q={encoded}"
        webbrowser.open(url)
        return f"Đang tìm kiếm {query} trên Google."

# -------------------------------------------------------------
# 3. GÕ VĂN BẢN BẰNG GIỌNG NÓI (VOICE DICTATION)
# -------------------------------------------------------------

def type_text_to_cursor(text):
    """
    Gõ trực tiếp văn bản tiếng Việt có dấu vào bất kỳ vị trí con trỏ chuột nào
    (Word, Zalo, Messenger, VS Code...) sử dụng clipboard an toàn 100%.
    """
    if not text:
        return "Không có nội dung văn bản để gõ."
    try:
        # Sử dụng tkinter tạm để đưa văn bản vào clipboard Windows
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()

        # Dán vào vị trí con trỏ hiện thời
        time.sleep(0.1)
        keyboard.send("ctrl+v")
        return f"Đã gõ: \"{text[:30]}...\""
    except Exception as e:
        return f"Lỗi khi gõ văn bản: {e}"

# -------------------------------------------------------------
# 4. CHẾ ĐỘ LẬP TRÌNH ANTIGRAVITY CLI
# -------------------------------------------------------------

def launch_antigravity_cli(prompt, agy_path=None):
    """Mở cửa sổ Antigravity CLI độc lập để lập trình viên làm việc chuyên sâu"""
    if not agy_path:
        agy_path = os.path.expanduser(r"~/.gemini/bin/agy.exe")
        if not os.path.exists(agy_path):
            agy_path = "agy"

    try:
        cmd = f'"{agy_path}" -i "{prompt}"'
        subprocess.Popen(f'start "Antigravity CLI - Alex" cmd.exe /k {cmd}', shell=True)
        return "Đang mở cửa sổ Antigravity CLI để hỗ trợ lập trình."
    except Exception as e:
        return f"Không thể khởi chạy Antigravity CLI: {e}"
