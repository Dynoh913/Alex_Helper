import re
import difflib

# ----------------------------------------------------------------------
# 1. BẢNG PHIÊN ÂM VÀ LỖI ÂM HỌC ASR (PHONETIC & SPEECH-TO-TEXT MAP)
# ----------------------------------------------------------------------
PHONETIC_ASR_RULES = [
    # Ứng dụng & Nền tảng quốc tế (Người Việt thường đọc phiên âm)
    (r"\b(?:du\s*túp|diu\s*túp|dút\s*túp|u\s*túp|u\s*tube|giu\s*túp|du\s*tube|dâu\s*túp|dô\s*túp)\b", "youtube"),
    (r"\b(?:sờ\s*po\s*ti\s*phai|sờ\s*po\s*ti|xì\s*po\s*ti|pót\s*ti\s*phai|spoti|sờ\s*pót\s*ti)\b", "spotify"),
    (r"\b(?:dinh\s*em\s*pi\s*ba|dinh\s*mp3|dim\s*mp3|zing\s*em\s*pi\s*ba|dinh\s*mp\s*3)\b", "zing mp3"),
    (r"\b(?:phây\s*búc|fây\s*búc|phây|phe\s*búc|fây|phét\s*búc|face\s*book)\b", "facebook"),
    (r"\b(?:gúc\s*gồ|gút\s*gồ|gu\s*gồ|gúc|gồ|gâu\s*gồ)\b", "google"),
    (r"\b(?:cờ\s*rôm|chờ\s*rôm|khờ\s*rôm|rôm|crôm)\b", "chrome"),
    (r"\b(?:vê\s*ét\s*code|vi\s*ét\s*code|vét\s*code|vê\s*ét)\b", "vs code"),
    (r"\b(?:án\s*ti\s*gra\s*vi\s*ti|ăng\s*ti\s*gra\s*vi\s*ti|en\s*ti\s*gra\s*vi\s*ti|an\s*ti\s*gravity|an\s*ti\s*gra)\b", "antigravity"),
    (r"\b(?:cốc\s*cốc|cóc\s*cóc|cộc\s*cộc)\b", "cốc cốc"),
    (r"\b(?:méc\s*xên\s*dơ|mét\s*xên\s*dơ|méc\s*xen\s*dơ|mess)\b", "messenger"),
    (r"\b(?:tóp\s*tóp|tóp\s*top|tíc\s*tóc)\b", "tiktok"),

    # Lỗi nhận diện hành động ASR phổ biến (Google Voice thường nghe nhầm)
    (r"^(?:clickbuy|click\s*buy|click\s*bài|clic\s*bài|play\s*bài|play)\s*(?:bài)?\b", "bật bài"),
    (r"\b(?:bậc\s*bài|bặt\s*bài|bậy\s*bài|bập\s*bài)\b", "bật bài"),
    (r"\b(?:mợ\s*bài|mở\s*bái|mở\s*bái\s*hát)\b", "mở bài"),
    (r"\b(?:tắt\s*táp|đóng\s*táp|tắt\s*tháp|đóng\s*tháp|tắt\s*tab|đóng\s*tab)\b", "đóng tab"),
    (r"\b(?:đét\s*tốp|đét\s*tóp|đề\s*tốc|đéc\s*tốp|đéc\s*tóp)\b", "desktop"),
    (r"\b(?:sờ\s*krin\s*sót|sờ\s*cơ\s*rin\s*sót|chụp\s*màn\s*hinh)\b", "chụp màn hình"),
    (r"\b(?:nếch\s*bài|nhếch\s*bài|nếch|nhếch)\b", "chuyển bài"),
    (r"\b(?:pau\s*nhạc|pô\s*nhạc|pâu\s*nhạc|pót\s*nhạc|pau)\b", "tạm dừng nhạc"),
    (r"\b(?:tua\s*bài|lùi\s*bài|bài\s*trưóc)\b", "bài trước"),

    # Sửa lỗi chính tả không dấu / gõ nhầm thông dụng
    (r"\b(?:am\s*luong|am\s*lượng|âm\s*luong)\b", "âm lượng"),
    (r"\b(?:do\s*sang|do\s*sáng|độ\s*sang)\b", "độ sáng"),
    (r"\b(?:man\s*hinh|man\s*hình|màn\s*hinh)\b", "màn hình"),
    (r"\b(?:chup\s*anh|chụp\s*anh|chup\s*ảnh)\b", "chụp ảnh"),
    (r"\b(?:tat\s*tieng|tắt\s*tieng|tat\s*tiếng)\b", "tắt tiếng"),
    (r"\b(?:khoa\s*may|khoa\s*máy|khoá\s*máy)\b", "khóa máy"),
    (r"\b(?:may\s*gio|may\s*giờ|mấy\s*gio)\b", "mấy giờ"),
    (r"\b(?:kiem\s*tra\s*pin|kiem\s*tra|kiểm\s*tra\s*pin)\b", "kiểm tra pin"),
    (r"\b(?:lap\s*trinh|lập\s*trinh|viet\s*code|viết\s*cốt)\b", "lập trình"),
]

# ----------------------------------------------------------------------
# 2. BẢNG TỪ ĐIỂN TỪ KHÓA CHUẨN ĐỂ SO KHỚP MỜ (FUZZY DICTIONARY)
# ----------------------------------------------------------------------
STANDARD_DICTIONARY = {
    "youtube": ["yotube", "youtobe", "youtub", "youtebe", "you tube", "yutube", "youtubee"],
    "spotify": ["spotifi", "spotyfi", "spootify", "spotfy", "spotiify"],
    "chrome": ["chorme", "crome", "chrom", "chroome"],
    "facebook": ["facebok", "facbook", "fecebook", "faecbook"],
    "google": ["gogle", "googel", "googl", "goolge"],
    "antigravity": ["antigraviti", "antigravty", "antigravti", "antigravitty"],
    "desktop": ["destop", "desktp", "deskop", "dektop"],
    "screenshot": ["screenshit", "screenshoot", "screenshop"],
    "calculator": ["calcutor", "caculator", "calculater"],
    "notepad": ["notepd", "notpad", "nodepad"]
}

def fuzzy_correct_tokens(text):
    """Sửa lỗi chính tả từng từ dựa trên thuật toán so khớp mờ Levenshtein/difflib"""
    words = text.split()
    corrected_words = []
    
    for w in words:
        w_lower = w.lower()
        matched = False
        
        # Kiểm tra bảng biến thể đã đăng ký
        for target, variants in STANDARD_DICTIONARY.items():
            if w_lower in variants:
                corrected_words.append(target)
                matched = True
                break
            # Nếu từ đủ dài (>= 4 ký tự), kiểm tra khoảng cách ký tự (cutoff 78%)
            if len(w_lower) >= 4:
                matches = difflib.get_close_matches(w_lower, [target], n=1, cutoff=0.78)
                if matches:
                    corrected_words.append(target)
                    matched = True
                    break
        
        if not matched:
            corrected_words.append(w)
            
    return " ".join(corrected_words)

# ----------------------------------------------------------------------
# 3. HÀM CHÍNH: TIÊN ĐOÁN VÀ SỬA LỖI CHÍNH TẢ TRƯỚC KHI INPUT VÀO BRAIN
# ----------------------------------------------------------------------
def predict_and_correct(text):
    """
    Tiên đoán và sửa lỗi chính tả, phiên âm, ngọng giọng nói ASR trước khi đưa vào Brain:
    - Trả về: (text_đã_sửa, có_sửa_đổi_hay_không)
    """
    if not text:
        return "", False
        
    original = text.strip()
    current = original.lower()
    
    # Bước 1: Áp dụng các quy tắc âm học & phiên âm tiếng Việt ASR
    for pattern, replacement in PHONETIC_ASR_RULES:
        current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)
    
    # Bước 2: Sửa lỗi chính tả mờ (Fuzzy matching)
    current = fuzzy_correct_tokens(current)
    
    # Bước 3: Chuẩn hóa khoảng trắng thừa
    current = re.sub(r"\s+", " ", current).strip()
    
    is_modified = (current.lower() != original.lower())
    return current, is_modified
