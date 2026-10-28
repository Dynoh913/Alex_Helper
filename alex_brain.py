import os
import re
import requests
import subprocess
import alex_actions

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

def clean_command(text):
    """
    Chuẩn hóa câu lệnh tiếng Việt:
    - Loại bỏ dấu câu thừa ở đầu/cuối
    - Loại bỏ tiền tố xưng hô, khẩu ngữ (ví dụ: 'bảo mở...', 'hãy mở...', 'alex ơi...')
    - Loại bỏ hậu tố khẩu ngữ (ví dụ: '...cho tôi', '...giùm tôi', '...đi', '...nhé')
    """
    if not text:
        return ""
    cmd = text.lower().strip()
    cmd = re.sub(r"^[\,\.\?\!\:\;]+|[\,\.\?\!\:\;]+$", "", cmd).strip()
    
    prefix_patterns = [
        r"^(?:alex\s*ơi|hey\s*alex|alex)\s*",
        r"^(?:bảo|hãy|làm\s*ơn|vui\s*lòng|nhờ\s*bạn|phiền\s*bạn)\s*",
        r"^(?:giúp\s*mình|giúp\s*tôi|hộ\s*mình|hộ\s*tôi|giùm\s*mình|giùm\s*tôi)\s*",
        r"^(?:cho\s*mình|cho\s*tôi|tôi\s*muốn|mình\s*muốn|muốn)\s*",
        r"^(?:bạn\s*ơi|em\s*ơi)\s*"
    ]
    changed = True
    while changed:
        changed = False
        for p in prefix_patterns:
            new_cmd = re.sub(p, "", cmd).strip()
            if new_cmd != cmd:
                cmd = new_cmd
                changed = True

    suffix_patterns = [
        r"\s+(?:cho\s*mình|cho\s*tôi|giúp\s*mình|giúp\s*tôi|giùm\s*tôi|giùm\s*mình|hộ\s*tôi|hộ\s*mình)$",
        r"\s+(?:với\s*nhé|với\s*nào|với|nhé|nha|đi|lên|nào|được\s*không|giùm|hộ)$"
    ]
    changed = True
    while changed:
        changed = False
        for p in suffix_patterns:
            new_cmd = re.sub(p, "", cmd).strip()
            if new_cmd != cmd:
                cmd = new_cmd
                changed = True

    return cmd

def ask_gemini_ai(prompt):
    """Truy vấn câu hỏi tổng quát với Gemini Flash AI siêu tốc (trả lời ngắn gọn 1-2 câu tiếng Việt)"""
    if not GEMINI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    system_instruction = (
        "Bạn là Alex, trợ lý ảo thông minh trên máy tính Windows. "
        "Hãy trả lời người dùng một cách thân thiện, chính xác, cực kỳ ngắn gọn (chỉ 1 hoặc 2 câu) "
        "để phát âm rõ ràng qua giọng nói. Tuyệt đối không dùng ký tự markdown như sao chép, ngoặc, gạch đầu dòng."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }

    try:
        resp = requests.post(url, json=payload, timeout=12)
        if resp.status_code == 200:
            candidates = resp.json().get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text = re.sub(r'[\*\#\_\[\]\`]', '', text).strip()
                return text
        else:
            # Fallback sang gemini-flash-latest
            url_fb = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
            resp_fb = requests.post(url_fb, json=payload, timeout=10)
            if resp_fb.status_code == 200:
                text = resp_fb.json().get("candidates", [])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text = re.sub(r'[\*\#\_\[\]\`]', '', text).strip()
                return text
    except Exception:
        pass
    return None

def ask_antigravity_headless(prompt):
    """Dự phòng: Chạy agy -p (print mode) ngầm không bật cửa sổ dòng lệnh"""
    try:
        agy_path = os.path.expanduser(r"~/.gemini/bin/agy.exe")
        if not os.path.exists(agy_path):
            agy_path = "agy"
        res = subprocess.run(
            [agy_path, "-p", f"Trả lời cực kỳ ngắn gọn 1 câu tiếng Việt: {prompt}"],
            capture_output=True,
            text=True,
            timeout=20,
            encoding="utf-8",
            errors="ignore"
        )
        lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip() and not l.startswith("Hey,") and "───" not in l]
        if lines:
            return lines[-1]
    except Exception:
        pass
    return None

def process_command(command_text, agy_path=None):
    """
    XỬ LÝ VÀ ĐIỀU PHỐI LỆNH TỔNG THỂ (BRAIN ROUTER):
    Trả về dictionary cấu trúc chuẩn:
    {
        "type": "system" | "app" | "dictation" | "ai" | "antigravity",
        "title": "Tên hành động ngắn",
        "speech": "Lời thoại Alex sẽ phát âm",
        "hud_sub": "Mô tả phụ cho giao diện HUD"
    }
    """
    raw_cmd = command_text.lower().strip()
    cmd = clean_command(command_text)

    # 1. GÕ VĂN BẢN TRỰC TIẾP (VOICE DICTATION)
    # Ví dụ: "Gõ: Chào bạn", "Nhập: Hôm nay họp lúc 2 giờ", "Gõ cho tôi nội dung..."
    dictation_match = re.match(r"^(?:gõ|nhập|viết|soạn)\s*(?:cho tôi|cho mình|văn bản|nội dung|:\s*)?\s*(.+)$", cmd)
    if dictation_match and any(w in cmd[:8] for w in ["gõ", "nhập", "viết", "soạn"]):
        content_to_type = dictation_match.group(1).strip()
        if content_to_type:
            res = alex_actions.type_text_to_cursor(content_to_type)
            return {
                "type": "dictation",
                "title": "Đã gõ văn bản",
                "speech": "Đã gõ văn bản vào ứng dụng cho bạn.",
                "hud_sub": f"\"{content_to_type[:40]}...\""
            }

    # 2. XEM GIỜ & NGÀY THÁNG
    if any(k in cmd for k in ["mấy giờ", "thời gian", "bây giờ là mấy giờ", "ngày mấy", "ngày bao nhiêu", "hôm nay thứ mấy"]):
        info = alex_actions.get_time_date_info()
        return {
            "type": "system",
            "title": "Xem giờ & Ngày",
            "speech": info,
            "hud_sub": info
        }

    # 3. KIỂM TRA PIN
    if any(k in cmd for k in ["kiểm tra pin", "pin còn bao nhiêu", "mức pin", "thời lượng pin", "pin máy tính", "xem pin"]):
        info = alex_actions.get_battery_info()
        return {
            "type": "system",
            "title": "Kiểm tra pin laptop",
            "speech": info,
            "hud_sub": info
        }

    # 4. ĐIỀU KHIỂN ÂM LƯỢNG
    if any(k in cmd for k in ["tăng âm lượng", "tăng tiếng", "to lên", "bật to lên", "cho to"]):
        res = alex_actions.change_volume("up")
        return {"type": "system", "title": "Âm lượng", "speech": res, "hud_sub": "Đã tăng thêm 5 mức"}

    if any(k in cmd for k in ["giảm âm lượng", "giảm tiếng", "nhỏ lại", "nhỏ bớt", "cho nhỏ"]):
        res = alex_actions.change_volume("down")
        return {"type": "system", "title": "Âm lượng", "speech": res, "hud_sub": "Đã giảm bớt 5 mức"}

    if any(k in cmd for k in ["tắt tiếng", "im lặng", "mute", "bật lại tiếng", "bật tiếng"]):
        res = alex_actions.change_volume("mute")
        return {"type": "system", "title": "Âm lượng", "speech": res, "hud_sub": "Chuyển trạng thái bật/tắt tiếng"}

    # 5. ĐIỀU CHỈNH ĐỘ SÁNG MÀN HÌNH
    if any(k in cmd for k in ["tăng độ sáng", "sáng hơn", "màn hình tối quá"]):
        res = alex_actions.change_brightness("up")
        return {"type": "system", "title": "Độ sáng màn hình", "speech": res, "hud_sub": res}

    if any(k in cmd for k in ["giảm độ sáng", "tối bớt", "màn hình sáng quá"]):
        res = alex_actions.change_brightness("down")
        return {"type": "system", "title": "Độ sáng màn hình", "speech": res, "hud_sub": res}

    # 6. QUẢN LÝ CỬA SỔ & MÀN HÌNH
    if any(k in cmd for k in ["chụp màn hình", "chụp ảnh màn hình", "screenshot", "cắt màn hình"]):
        res = alex_actions.take_screenshot()
        return {"type": "system", "title": "Chụp màn hình", "speech": res, "hud_sub": "Đã mở Windows Snipping Tool"}

    if any(k in cmd for k in ["hiện desktop", "về màn hình chính", "màn hình chính", "ẩn hết cửa sổ", "thu nhỏ tất cả", "ra desktop", "ra ngoài desktop"]):
        res = alex_actions.show_desktop()
        return {"type": "system", "title": "Màn hình Desktop", "speech": res, "hud_sub": "Đã thu nhỏ các cửa sổ"}

    if any(k in cmd for k in ["đóng cửa sổ", "tắt ứng dụng", "đóng ứng dụng", "tắt tab", "đóng tab"]):
        res = alex_actions.close_active_window()
        return {"type": "system", "title": "Đóng cửa sổ", "speech": res, "hud_sub": "Đã gửi Alt+F4"}

    if any(k in cmd for k in ["khóa máy", "khóa màn hình", "lock pc"]):
        res = alex_actions.lock_computer()
        return {"type": "system", "title": "Khóa máy tính", "speech": res, "hud_sub": "Bảo mật hệ thống"}

    # 7. CHẾ ĐỘ LẬP TRÌNH ANTIGRAVITY (Ưu tiên cao hơn mở app thông thường)
    antigravity_keywords = [
        "antigravity", "mở agy", "bật agy", "chạy agy", "dùng agy",
        "lập trình", "viết code", "sửa code", "fix bug",
        "tạo dự án", "refactor code", "viết script"
    ]
    if any(k in cmd for k in antigravity_keywords):
        res = alex_actions.launch_antigravity_cli(command_text, agy_path=agy_path)
        return {
            "type": "antigravity",
            "title": "Antigravity CLI",
            "speech": "Đang mở Antigravity CLI để hỗ trợ bạn lập trình.",
            "hud_sub": "Mở cửa sổ lập trình chuyên sâu"
        }

    # 8. YOUTUBE (XỬ LÝ TOÀN DIỆN: TÌM KIẾM VIDEO HOẶC MỞ TRỰC TIẾP)
    if "youtube" in cmd:
        yt_search_patterns = [
            r"(?:tìm kiếm|tìm|bật|mở|phát|nghe|xem)\s*(?:bài hát|bài|video|nhạc|clip|nội dung|phim)?\s*(.+?)\s*(?:trên|ở|qua|bằng)\s*youtube",
            r"(?:trên|ở)\s*youtube\s*(?:tìm kiếm|tìm|bật|mở|phát|nghe|xem)?\s*(?:bài hát|bài|video|nhạc|clip|nội dung|phim)?\s*(.+)",
            r"youtube\s+(?:tìm kiếm|tìm|bật|mở|phát|nghe|xem)\s*(?:bài hát|bài|video|nhạc|clip)?\s*(.+)",
        ]
        query = None
        for pat in yt_search_patterns:
            m = re.search(pat, cmd)
            if m:
                extracted = m.group(1).strip()
                if extracted and extracted not in ["trang web", "web", "ứng dụng", "nghe nhạc", "xem", "cho tôi"]:
                    query = extracted
                    break

        if query:
            res = alex_actions.search_google_or_youtube(query, target="youtube")
            return {"type": "app", "title": "Tìm kiếm YouTube", "speech": res, "hud_sub": f"Từ khóa: {query}"}
        else:
            res = alex_actions.open_web_or_app("youtube")
            return {"type": "app", "title": "Mở YouTube", "speech": "Đã mở YouTube trên trình duyệt.", "hud_sub": "https://www.youtube.com"}

    # 9. TÌM KIẾM GOOGLE
    google_search_patterns = [
        r"^(?:tìm kiếm|tra cứu|tìm trên mạng|google)\s*(?:cho tôi|cho mình|về|cái)?\s*(.+)$",
        r"(?:tìm kiếm|tra cứu|tìm)\s+(.+?)\s+(?:trên|ở)\s*google",
    ]
    for pat in google_search_patterns:
        m = re.search(pat, cmd)
        if m:
            q = m.group(1).strip()
            if q and q not in ["trang web", "web", "ứng dụng"]:
                res = alex_actions.search_google_or_youtube(q, target="google")
                return {"type": "app", "title": "Tìm kiếm Google", "speech": res, "hud_sub": f"Từ khóa: {q}"}

    # 10. MỞ ỨNG DỤNG HOẶC TRANG WEB THÔNG THƯỜNG
    target_clean = re.sub(r"^(?:mở|bật|vào|khởi động|truy cập|lên|xem)\s*(?:trang web|trang|ứng dụng|phần mềm|app)?\s*", "", cmd).strip()
    
    # A. Khớp trang web
    for site_key in alex_actions.COMMON_WEBSITES:
        if site_key in target_clean or site_key == cmd:
            res = alex_actions.open_web_or_app(site_key)
            return {"type": "app", "title": f"Mở {site_key.title()}", "speech": res, "hud_sub": res}

    # B. Khớp ứng dụng
    for app_key in alex_actions.COMMON_APPS:
        if app_key in target_clean or app_key == cmd:
            res = alex_actions.open_web_or_app(app_key)
            return {"type": "app", "title": f"Mở {app_key.title()}", "speech": res, "hud_sub": res}

    # C. Nếu câu nói bắt đầu bằng từ khóa mở/bật/vào ứng dụng chung
    open_fallback_match = re.match(r"^(?:mở|bật|vào|khởi động)\s*(?:ứng dụng|phần mềm|trang web|trang)?\s*(.+)$", cmd)
    if open_fallback_match:
        target_name = open_fallback_match.group(1).strip()
        res = alex_actions.open_web_or_app(target_name)
        return {"type": "app", "title": f"Mở {target_name.title()}", "speech": res, "hud_sub": res}

    # 11. TRẢ LỜI KIẾN THỨC BẰNG GEMINI AI (SIÊU TỐC, KHÔNG MỞ CỬA SỔ)
    ai_answer = ask_gemini_ai(command_text)
    if not ai_answer:
        ai_answer = ask_antigravity_headless(command_text)

    if ai_answer:
        return {
            "type": "ai",
            "title": "Alex AI",
            "speech": ai_answer,
            "hud_sub": ai_answer[:60] + "..." if len(ai_answer) > 60 else ai_answer
        }

    return {
        "type": "unknown",
        "title": "Alex chưa hiểu",
        "speech": "Alex chưa nghe rõ yêu cầu, bạn có thể nói lại được không?",
        "hud_sub": f"\"{command_text}\""
    }
