import os
import re
import json
import time
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
CANDIDATE_MODELS = ["gemini-3.5-flash"]

SYSTEM_PROMPT = """Bạn là Bộ Não Suy Luận Ngữ Nghĩa AI (Semantic Reasoning Engine) của Trợ lý ảo Alex trên Windows.
Nhiệm vụ: Phân tích câu nói bằng ngôn ngữ tự nhiên của người dùng (kể cả nói ngọng, nói méo âm ASR, viết tắt, tiếng lóng, câu nói gián tiếp, ẩn dụ hoặc nhiều tầng nghĩa) và SUY LUẬN Ý ĐỊNH ĐIỀU KHIỂN HỆ THỐNG HOẶC HỎI ĐÁP.

DANH MỤC ACTION VÀ TARGET HỢP LỆ:
1. play_music:
   - target: Tên bài hát, ca khúc, video hoặc thể loại nhạc đã được làm sạch, bỏ từ thừa (VD: "Sóng Gió", "Hoa Hải Đường Jack", "nhạc lofi chill").
   - platform: "youtube" | "spotify" | "zingmp3" | "ask" (nếu người dùng không chỉ rõ nền tảng thì để "ask").
2. control_media:
   - target: "play_pause" (tạm dừng/tiếp tục) | "next" (chuyển bài) | "prev" (lùi bài) | "stop" (dừng hẳn)
3. system_volume:
   - target: "up" (tăng âm lượng, loa bé, cho to lên) | "down" (giảm âm lượng, ồn quá, cho nhỏ) | "mute" (tắt tiếng, im lặng)
4. system_brightness:
   - target: "up" (tăng độ sáng, tối quá, nhìn không rõ) | "down" (giảm độ sáng, chói mắt quá, sáng quá)
5. system_window:
   - target: "desktop" (hiện màn hình chính, ẩn hết cửa sổ, tắt hết tab để làm việc) | "close" (đóng cửa sổ, tắt app này) | "screenshot" (chụp màn hình, cắt màn hình) | "lock" (khóa máy, khóa màn hình)
6. system_info:
   - target: "battery" (pin còn bao nhiêu, bao nhiêu phần trăm điện) | "time" (mấy giờ, ngày tháng hôm nay)
7. open_app:
   - target: Mã ứng dụng ngắn gọn (vd: "word", "excel", "chrome", "zalo", "spotify", "notepad", "calc", "code", "settings")
8. open_website:
   - target: Tên trang web (vd: "facebook", "youtube", "chatgpt", "google", "dantri")
9. search_web:
   - target: Từ khóa tìm kiếm trên Google đã làm sạch
10. dictation:
    - target: Đoạn văn bản người dùng muốn gõ/nhập vào con trỏ chuột
11. preference:
    - target: "spotify" | "youtube" | "zingmp3" | "ask" (khi người dùng muốn cài đặt nền tảng mặc định)
12. antigravity:
    - target: Yêu cầu lập trình, viết code, sửa lỗi phần mềm
13. greeting:
    - target: null (người dùng chỉ gọi tên "Alex", chào hỏi, hỏi "có đó không")
14. general_qa:
    - target: Câu trả lời ngắn gọn 1-2 câu tiếng Việt (không dùng dấu markdown *, #, _) giải đáp thắc mắc người dùng
15. unknown:
    - target: null (tiếng ồn vô nghĩa, không thể suy luận)

QUY TẮC SUY LUẬN NGỮ NGHĨA (SEMANTIC REASONING):
- Hiểu được các lỗi âm học tiếng Việt phổ biến:
  + "Clickbuy bài sóng gió trên du túp" -> ASR nhận âm Click bài -> Clickbuy, du túp -> YouTube => action: play_music, target: "Sóng Gió", platform: "youtube".
  + "sờ po ti phai" -> Spotify, "dinh mp3" -> Zing MP3.
- Hiểu câu nói gián tiếp / trạng thái cảm xúc:
  + "chói mắt quá Alex ơi" / "sáng chói cả mắt" => action: system_brightness, target: "down".
  + "loa bé quá cho to lên tí" / "nghe không rõ cho to lên" => action: system_volume, target: "up".
  + "tắt hết cửa sổ đi để tao làm việc" / "về màn hình chính" => action: system_window, target: "desktop".
  + "máy tính còn bao nhiêu phần trăm điện" => action: system_info, target: "battery".
  + "cho tớ nghe cái bài gì của Jack mà có hoa hải đường ấy" => action: play_music, target: "Hoa Hải Đường Jack", platform: "ask".

CHỈ XUẤT RA DUY NHẤT 1 ĐỐI TƯỢNG JSON (Không kèm markdown ```json hay văn bản thừa):
{
  "action": "...",
  "target": "...",
  "platform": "...",
  "speech": "...",
  "reasoning": "Tóm tắt 1 câu ngắn gọn tại sao AI suy luận như vậy"
}"""

def parse_intent_with_ai(user_command: str, timeout: float = 2.5) -> dict:
    """
    Sử dụng Gemini AI để suy luận ngữ nghĩa của câu lệnh người dùng.
    Trả về dict chuẩn hóa:
    {
        "action": str,
        "target": str or None,
        "platform": str or None,
        "speech": str or None,
        "reasoning": str
    }
    Trả về None nếu có lỗi mạng hoặc quá thời gian timeout (để rơi về Tier 2 fallback).
    """
    if not GEMINI_API_KEY or not user_command or not user_command.strip():
        return None

    cmd_text = user_command.strip()
    payload = {
        "contents": [{"parts": [{"text": cmd_text}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1,
            "maxOutputTokens": 256
        }
    }

    for model_name in CANDIDATE_MODELS:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            resp = requests.post(
                api_url,
                json=payload,
                headers={"Connection": "close"},
                timeout=timeout
            )
            if resp.status_code == 200:
                result_json = resp.json()
                candidates = result_json.get("candidates", [])
                if candidates:
                    raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    # Loại bỏ backticks nếu mô hình vẫn sinh ra markdown
                    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                    raw_text = re.sub(r"\s*```$", "", raw_text)
                    data = json.loads(raw_text)
                    if isinstance(data, dict) and "action" in data:
                        return data
        except Exception:
            continue

    return None
