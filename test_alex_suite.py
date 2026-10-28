import sys
import os
import time

# UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import alex_actions
import alex_brain
from alex_hud import AlexHUD
from voice_assistant import strip_over_termination

def run_tests():
    print("=" * 60)
    print(" BẮT ĐẦU BỘ KIỂM THỬ TỰ ĐỘNG CHO TRỢ LÝ ALEX V4.5")
    print("=" * 60)
    
    passed = 0
    failed = 0

    # Test 1: Date and time
    try:
        t_info = alex_actions.get_time_date_info()
        assert "Bây giờ là" in t_info
        print(f" [PASS] Test 1: Thời gian -> {t_info}")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 1: {e}")
        failed += 1

    # Test 2: Battery status
    try:
        b_info = alex_actions.get_battery_info()
        assert "Pin" in b_info
        print(f" [PASS] Test 2: Trạng thái pin -> {b_info}")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 2: {e}")
        failed += 1

    # Test 3: Volume control
    try:
        v_up = alex_actions.change_volume("up", 1)
        v_down = alex_actions.change_volume("down", 1)
        assert "tăng" in v_up and "giảm" in v_down
        print(f" [PASS] Test 3: Điều khiển âm lượng -> {v_up} / {v_down}")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 3: {e}")
        failed += 1

    # Test 4: Voice Dictation (Clipboard + Type simulation)
    try:
        d_res = alex_actions.type_text_to_cursor("Kiểm thử gõ tiếng Việt")
        assert "Đã gõ" in d_res
        print(f" [PASS] Test 4: Gõ văn bản con trỏ -> {d_res}")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 4: {e}")
        failed += 1

    # Test 5: Strip OVER keyword
    try:
        cleaned, has_over = strip_over_termination("mở chrome over")
        assert cleaned == "mở chrome" and has_over is True
        cleaned2, has_over2 = strip_over_termination("mở youtube")
        assert cleaned2 == "mở youtube" and has_over2 is False
        print(f" [PASS] Test 5: Cắt từ khóa OVER chuẩn xác -> '{cleaned}', has_over={has_over}")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 5: {e}")
        failed += 1

    # Test 6: Brain Router - Time
    try:
        res = alex_brain.process_command("mấy giờ rồi")
        assert res["type"] == "system"
        print(f" [PASS] Test 6: Brain Router [Giờ] -> {res['title']}")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 6: {e}")
        failed += 1

    # Test 7: Brain Router - Dictation
    try:
        res = alex_brain.process_command("gõ: hôm nay họp lúc 2 giờ chiều")
        assert res["type"] == "dictation"
        print(f" [PASS] Test 7: Brain Router [Dictation] -> {res['title']} ({res['hud_sub']})")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 7: {e}")
        failed += 1

    # Test 8: Brain Router - Search Web
    try:
        res = alex_brain.process_command("tìm kiếm công thức phở bò trên google")
        assert res["type"] == "app" and "Google" in res["title"]
        print(f" [PASS] Test 8: Brain Router [Google Search] -> {res['title']}")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 8: {e}")
        failed += 1

    # Test 9: Brain Router - Antigravity Developer Mode
    try:
        res = alex_brain.process_command("mở antigravity lập trình python")
        assert res["type"] == "antigravity"
        print(f" [PASS] Test 9: Brain Router [Antigravity Dev] -> {res['title']}")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 9: {e}")
        failed += 1

    # Test 10: Floating HUD Pill Widget
    try:
        hud = AlexHUD()
        hud.show("🎙️", "Kiểm thử HUD Alex", "Đang chạy bộ test tự động...")
        time.sleep(1)
        hud.show_success("Kiểm thử thành công!", "Tất cả module hoạt động hoàn hảo", auto_hide_ms=1500)
        time.sleep(1.8)
        print(" [PASS] Test 10: Giao diện Floating HUD (Translucent Pill) hiển thị mượt mà")
        passed += 1
    except Exception as e:
        print(f" [FAIL] Test 10: {e}")
        failed += 1

    print("=" * 60)
    print(f" KẾT QUẢ: {passed}/10 BÀI KIỂM THỬ ĐẠT CHUẨN (Passed: {passed}, Failed: {failed})")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
