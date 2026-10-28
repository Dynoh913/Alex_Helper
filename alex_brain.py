import os
import re
import requests
import subprocess
import alex_actions
import alex_config

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
    """Truy vấn câu hỏi tổng quát với Gemini Flash AI siêu tốc (timeout 4s chống đơ)"""
    if not GEMINI_API_KEY:
        return None

    candidate_models = ["gemini-3.5-flash", "gemini-3.5-flash-lite"]
    system_instruction = (
        "Bạn là Alex, trợ lý ảo thông minh trên máy tính Windows. "
        "Hãy trả lời người dùng một cách thân thiện, chính xác, cực kỳ ngắn gọn (chỉ 1 hoặc 2 câu) "
        "để phát âm rõ ràng qua giọng nói. Tuyệt đối không dùng ký tự markdown như sao chép, ngoặc, gạch đầu dòng."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }

    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            resp = requests.post(url, json=payload, timeout=4)
            if resp.status_code == 200:
                candidates = resp.json().get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    text = re.sub(r'[\*\#\_\[\]\`]', '', text).strip()
                    if text:
                        return text
        except Exception:
            continue
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

    # 6B. ĐIỀU KHIỂN PHÁT NHẠC TOÀN HỆ THỐNG (MEDIA PLAYBACK CONTROLS)
    if any(k in cmd for k in ["tạm dừng nhạc", "dừng nhạc", "dừng phát", "tạm dừng", "pause nhạc"]):
        res = alex_actions.media_control("play_pause")
        return {"type": "system", "title": "Tạm dừng nhạc", "speech": res, "hud_sub": "Media Play/Pause"}

    if any(k in cmd for k in ["tiếp tục phát", "bật lại nhạc", "phát tiếp", "tiếp tục nghe", "chơi tiếp"]):
        res = alex_actions.media_control("play_pause")
        return {"type": "system", "title": "Tiếp tục phát", "speech": res, "hud_sub": "Media Play/Pause"}

    if any(k in cmd for k in ["chuyển bài", "bài tiếp theo", "bài sau", "next bài", "bài kế tiếp"]):
        res = alex_actions.media_control("next")
        return {"type": "system", "title": "Bài tiếp theo", "speech": res, "hud_sub": "Next Track"}

    if any(k in cmd for k in ["bài trước", "quay lại bài trước", "lùi bài", "previous track"]):
        res = alex_actions.media_control("prev")
        return {"type": "system", "title": "Bài trước", "speech": res, "hud_sub": "Previous Track"}

    # 6C. CÀI ĐẶT SỞ THÍCH & CẤU HÌNH HỆ THỐNG (PREFERENCES)
    if re.search(r"(?:cài đặt|đặt|chọn)\s+.*(?:mặc định)", cmd) or "làm mặc định" in cmd:
        if "spotify" in cmd:
            alex_config.set_default_music_platform("spotify")
            return {"type": "system", "title": "Cài đặt mặc định", "speech": "Đã đặt Spotify làm nền tảng nghe nhạc mặc định của bạn.", "hud_sub": "Mặc định: Spotify"}
        elif "youtube" in cmd:
            alex_config.set_default_music_platform("youtube")
            return {"type": "system", "title": "Cài đặt mặc định", "speech": "Đã đặt YouTube làm nền tảng nghe nhạc mặc định của bạn.", "hud_sub": "Mặc định: YouTube"}
        elif "zing" in cmd:
            alex_config.set_default_music_platform("zingmp3")
            return {"type": "system", "title": "Cài đặt mặc định", "speech": "Đã đặt Zing MP3 làm nền tảng nghe nhạc mặc định của bạn.", "hud_sub": "Mặc định: Zing MP3"}
        elif "hỏi" in cmd:
            alex_config.set_default_music_platform("ask")
            return {"type": "system", "title": "Cài đặt mặc định", "speech": "Đã bật chế độ luôn hỏi trước khi phát nhạc.", "hud_sub": "Mặc định: Hỏi trước"}

    if cmd in ["hỏi trước khi bật nhạc", "hỏi trước khi phát nhạc", "hỏi nền tảng khi bật nhạc", "luôn hỏi nền tảng"]:
        alex_config.set_default_music_platform("ask")
        return {"type": "system", "title": "Cài đặt mặc định", "speech": "Đã bật chế độ luôn hỏi trước khi phát nhạc.", "hud_sub": "Mặc định: Hỏi trước"}

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

    # 8. PHÁT NHẠC, BÀI HÁT & VIDEO (MULTI-PLATFORM MEDIA & CLARIFICATION ROUTER)
    # A. Kiểm tra xem người dùng có chỉ định rõ nền tảng phát không
    # (Ví dụ: "bật bài sóng gió trên spotify", "mở sóng gió trên zing mp3", "nghe nhạc lofi trên youtube")
    specified_platform = None
    platform_label = "YouTube"
    if "spotify" in cmd:
        specified_platform = "spotify"
        platform_label = "Spotify"
    elif "zing" in cmd:
        specified_platform = "zingmp3"
        platform_label = "Zing MP3"
    elif "soundcloud" in cmd:
        specified_platform = "soundcloud"
        platform_label = "SoundCloud"
    elif "nhaccuatui" in cmd:
        specified_platform = "nhaccuatui"
        platform_label = "NhacCuaTui"
    elif "youtube" in cmd:
        specified_platform = "youtube"
        platform_label = "YouTube"

    if specified_platform:
        # Trích xuất từ khóa bài hát/nội dung
        pat = rf"(?:tìm kiếm|tìm|bật|mở|phát|nghe|xem)?\s*(?:bài\s*hát|bài\s*ca|bài|video|nhạc|clip|nội dung|phim)?\s*(.+?)\s*(?:trên|ở|qua|bằng)\s*(?:{specified_platform}|zing\s*mp3)"
        m = re.search(pat, cmd)
        query = None
        if m:
            extracted = m.group(1).strip()
            if extracted and extracted not in ["trang web", "web", "ứng dụng", "nghe nhạc", "xem", "cho tôi"]:
                query = extracted

        if not query:
            pat2 = rf"(?:trên|ở)?\s*(?:{specified_platform}|zing\s*mp3)\s*(?:tìm kiếm|tìm|bật|mở|phát|nghe|xem)?\s*(?:bài\s*hát|bài\s*ca|bài|video|nhạc|clip)?\s*(.+)"
            m2 = re.search(pat2, cmd)
            if m2:
                extracted = m2.group(1).strip()
                if extracted and extracted not in ["trang web", "web", "ứng dụng", "nghe nhạc", "xem", "cho tôi"]:
                    query = extracted

        if query:
            res = alex_actions.play_media_on_platform(query, platform=specified_platform)
            return {"type": "app", "title": f"{platform_label}: {query.title()}", "speech": res, "hud_sub": f"Từ khóa: {query}"}
        else:
            res = alex_actions.open_web_or_app(specified_platform)
            return {"type": "app", "title": f"Mở {platform_label}", "speech": f"Đã mở {platform_label}.", "hud_sub": f"https://www.{specified_platform}.com"}

    # B. Yêu cầu bật bài hát / phát nhạc tự nhiên nhưng CHƯA CHỈ ĐỊNH NỀN TẢNG
    # Ví dụ: "Bật bài sóng gió", "Mở bài hát lạc trôi", "Nghe nhạc lofi", "Phát ca khúc..."
    media_query = None
    music_match = re.match(r"^(?:bật|mở|nghe|phát|chơi)\s+(?:bài\s*hát|bài\s*ca|bài|ca\s*khúc|nhạc)\s*(.*)$", cmd)
    if music_match:
        media_query = music_match.group(1).strip()

    if not media_query:
        video_match = re.match(r"^(?:bật|mở|xem|chiếu|phát)\s+(?:video|clip|phim\s*hoạt\s*hình|phim)\s*(.*)$", cmd)
        if video_match:
            media_query = video_match.group(1).strip()

    if not media_query:
        direct_media_match = re.match(r"^(?:bài\s*hát|bài\s*ca|bài|ca\s*khúc|nhạc)\s+(.+)$", cmd)
        if direct_media_match:
            media_query = direct_media_match.group(1).strip()

    if not media_query and cmd in ["bật nhạc", "mở nhạc", "nghe nhạc", "phát nhạc", "bật bài hát", "mở bài hát"]:
        media_query = "nhạc hay"

    if media_query is not None:
        target_song = media_query if media_query and media_query not in ["hay", "nhẹ nhàng", "chill"] else "nhạc hay"
        default_plat = alex_config.get_default_music_platform()

        # NẾU CẤU HÌNH LÀ "ASK" -> KÍCH HOẠT HỘI THOẠI ĐA LƯỢT (CLARIFICATION DIALOGUE)
        if default_plat == "ask":
            song_display = f"bài {target_song}" if target_song != "nhạc hay" else "nhạc"
            return {
                "type": "clarify",
                "action": "play_music",
                "query": target_song,
                "title": f"Phát: {target_song.title()}",
                "speech": f"Bạn muốn nghe {song_display} trên YouTube, Spotify hay Zing MP3?",
                "hud_sub": "Đang chờ: YouTube / Spotify / Zing MP3"
            }
        else:
            # ĐÃ CÓ NỀN TẢNG MẶC ĐỊNH -> PHÁT THẲNG KHÔNG CẦN HỎI
            plat_name = "YouTube" if default_plat == "youtube" else ("Spotify" if default_plat == "spotify" else "Zing MP3")
            res = alex_actions.play_media_on_platform(target_song, platform=default_plat)
            return {
                "type": "app",
                "title": f"{plat_name}: {target_song.title()}",
                "speech": res,
                "hud_sub": f"Bài hát: {target_song}"
            }

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

    # 11. HỎI ĐÁP VỀ TRỢ LÝ ALEX (TỰ TRẢ LỜI NGAY TỨC THÌ 0s LATENCY)
    if any(w in cmd for w in ["tại sao", "sao", "vì sao"]) and any(w in cmd for w in ["không nghe", "không trả lời", "gọi"]):
        reply = "Tôi vẫn đang lắng nghe bạn. Bạn hãy nói to rõ hơn một chút hoặc dùng phím tắt Ctrl Alt Space nhé."
        return {"type": "ai", "title": "Alex Trả Lời", "speech": reply, "hud_sub": reply}

    if any(w in cmd for w in ["bạn là ai", "tên bạn là gì", "mày là ai", "mày tên gì"]):
        reply = "Tôi là Alex, trợ lý ảo thông minh giúp bạn điều khiển máy tính."
        return {"type": "ai", "title": "Alex Trả Lời", "speech": reply, "hud_sub": reply}

    if any(w in cmd for w in ["bạn làm được gì", "bạn có chức năng gì", "chức năng của bạn"]):
        reply = "Tôi có thể mở ứng dụng, tìm kiếm YouTube, tăng giảm âm lượng, kiểm tra pin, gõ văn bản và trả lời câu hỏi cho bạn."
        return {"type": "ai", "title": "Alex Trả Lời", "speech": reply, "hud_sub": reply}

    if any(w in cmd for w in ["khỏe không", "bạn có khỏe không"]):
        reply = "Tôi luôn khỏe và sẵn sàng phục vụ bạn."
        return {"type": "ai", "title": "Alex Trả Lời", "speech": reply, "hud_sub": reply}

    # 12. TRẢ LỜI KIẾN THỨC BẰNG GEMINI AI (SIÊU TỐC, TIMEOUT 4S)
    ai_answer = ask_gemini_ai(command_text)

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

def resolve_clarification(clarify_context, user_reply):
    """
    Xử lý câu trả lời tiếp theo của người dùng trong phiên hội thoại đa lượt (Multi-turn):
    - clarify_context: dict trả về từ turn trước (chứa action, query, v.v.)
    - user_reply: câu trả lời giọng nói của người dùng (ví dụ: 'Spotify', 'YouTube', 'Zing MP3 và đặt làm mặc định')
    """
    if not clarify_context or not isinstance(clarify_context, dict):
        return {"type": "app", "title": "Hoàn tất", "speech": "Đã xử lý yêu cầu.", "hud_sub": ""}

    action = clarify_context.get("action", "")
    query = clarify_context.get("query", "nhạc hay")
    reply = clean_command(user_reply).lower()

    if action == "play_music":
        platform = "youtube"
        plat_title = "YouTube"

        if "spotify" in reply:
            platform = "spotify"
            plat_title = "Spotify"
        elif "zing" in reply:
            platform = "zingmp3"
            plat_title = "Zing MP3"
        elif "soundcloud" in reply:
            platform = "soundcloud"
            plat_title = "SoundCloud"
        elif "nhaccuatui" in reply:
            platform = "nhaccuatui"
            plat_title = "NhacCuaTui"
        else:
            platform = "youtube"
            plat_title = "YouTube"

        # Nếu người dùng muốn ghi nhớ làm mặc định
        set_default_msg = ""
        if any(w in reply for w in ["mặc định", "luôn luôn", "lần sau", "mọi lần"]):
            alex_config.set_default_music_platform(platform)
            set_default_msg = f" Và Alex đã lưu {plat_title} làm nền tảng mặc định cho các lần sau."

        res = alex_actions.play_media_on_platform(query, platform=platform)
        speech_text = f"Đang mở {query} trên {plat_title}.{set_default_msg}"

        return {
            "type": "app",
            "title": f"{plat_title}: {query.title()}",
            "speech": speech_text,
            "hud_sub": f"Bài hát: {query}"
        }

    return {"type": "app", "title": "Thực thi", "speech": "Đang xử lý yêu cầu của bạn.", "hud_sub": ""}
