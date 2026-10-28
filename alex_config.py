import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alex_config.json")

DEFAULT_CONFIG = {
    "user_name": "Bạn",
    "default_music_platform": "ask",  # "ask", "youtube", "spotify", "zingmp3", "soundcloud"
    "auto_clarify_media": True,
    "volume_step": 5,
    "brightness_step": 15
}

def load_config():
    """Tải cấu hình người dùng từ alex_config.json, tạo mới nếu chưa có"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            # Điền các giá trị mặc định còn thiếu
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config_dict):
    """Lưu cấu hình người dùng vào file alex_config.json an toàn"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f" ⚠️ [LỖI CẤU HÌNH]: Không thể lưu config: {e}")
        return False

def get_default_music_platform():
    """Lấy nền tảng nghe nhạc mặc định ('ask', 'youtube', 'spotify', 'zingmp3')"""
    cfg = load_config()
    return cfg.get("default_music_platform", "ask")

def set_default_music_platform(platform):
    """Đặt nền tảng nghe nhạc mặc định"""
    cfg = load_config()
    cfg["default_music_platform"] = platform
    return save_config(cfg)
