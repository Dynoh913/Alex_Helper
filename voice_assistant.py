import os
import sys
import re
import time
import shutil
import datetime
import webbrowser
import urllib.parse
import collections
import threading
import audioop
import subprocess
import winsound
import ctypes
import numpy as np
import pyaudio
import requests
import speech_recognition as sr
from gtts import gTTS
import pygame
import keyboard
from openwakeword.model import Model

# Thiết lập UTF-8 cho console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Khởi tạo pygame mixer cho TTS
try:
    pygame.mixer.init()
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GLOBAL_HOTKEY = "ctrl+alt+space"

# Tự động tìm đường dẫn Antigravity CLI (agy) linh hoạt trên mọi máy tính
def get_antigravity_executable():
    """Tự động tìm agy trên PATH hoặc thư mục cài đặt mặc định của Antigravity"""
    agy_on_path = shutil.which("agy") or shutil.which("agy.exe")
    if agy_on_path:
        return agy_on_path

    default_gemini_path = os.path.expanduser(r"~/.gemini/bin/agy.exe")
    if os.path.exists(default_gemini_path):
        return default_gemini_path

    return "agy"

AGY_PATH = get_antigravity_executable()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# Ngưỡng kích hoạt mô hình Wake Word On-device (0.45 để cân bằng độ nhạy và chống kích hoạt nhầm)
WAKE_THRESHOLD = 0.45
HIGH_CONFIDENCE_THRESHOLD = 0.55

# Regex nhận diện và loại bỏ từ chốt câu "over"
OVER_TERMINATION_PATTERN = re.compile(
    r"\b(?:over|âu\s*vơ|ô\s*vơ)\b[\s\.\,\!\?]*$",
    re.IGNORECASE,
)

# Trạng thái điều phối hệ thống
is_processing = False
is_recording = False
stop_recording_event = threading.Event()
cancel_recording_event = threading.Event()
lock = threading.Lock()

def strip_over_termination(text):
    """Kiểm tra và cắt bỏ từ khóa kết thúc câu 'over' (hoặc 'âu vơ', 'ô vơ') ở cuối câu"""
    if not text:
        return text, False
    match = OVER_TERMINATION_PATTERN.search(text)
    if match:
        cleaned_text = OVER_TERMINATION_PATTERN.sub("", text).strip()
        return cleaned_text, True
    return text.strip(), False

def speak(text):
    """Phát âm giọng nói tiếng Việt tự nhiên (Thread-safe, đợi loa dứt hẳn)"""
    if not text:
        return
    print(f" 🗣️ [ALEX NÓI]: {text}")
    temp_file = os.path.join(BASE_DIR, f"temp_{int(time.time() * 1000)}.mp3")
    try:
        tts = gTTS(text=text, lang="vi", slow=False)
        tts.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        # Chờ thêm 0.3s sau khi phát xong để chống dội âm vào micro
        time.sleep(0.3)
    except Exception as e:
        print(f" ⚠️ [LỖI PHÁT ÂM]: {e}")
    finally:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception:
            pass

def play_beep(tone_type):
    """Phát âm thanh bíp phản hồi tức thì (Zero latency)"""
    try:
        if tone_type == "wake":
            winsound.Beep(1200, 70)
            winsound.Beep(1800, 90)
        elif tone_type == "ready":
            winsound.Beep(1400, 100)
        elif tone_type == "stop":
            winsound.Beep(1600, 80)
        elif tone_type == "cancel":
            winsound.Beep(400, 180)
        elif tone_type == "success":
            winsound.Beep(1500, 90)
            winsound.Beep(1800, 100)
        elif tone_type == "error":
            winsound.Beep(500, 200)
    except Exception:
        pass

def get_battery_info():
    """Lấy thông tin pin hệ thống Windows qua Windows API native"""
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
            return "Máy tính không có pin hoặc không xác định được trạng thái pin."
        ac_str = "đang cắm sạc nguồn" if s.AC == 1 else "đang sử dụng nguồn pin"
        return f"Pin máy tính hiện tại còn {s.Percent}%, {ac_str}."
    except Exception as e:
        return f"Không thể kiểm tra pin lúc này ({e})."

def get_date_time_info():
    """Trả về ngày giờ hiện tại bằng tiếng Việt chuẩn"""
    now = datetime.datetime.now()
    weekdays = ["thứ Hai", "thứ Ba", "thứ Tư", "thứ Năm", "thứ Sáu", "thứ Bảy", "Chủ Nhật"]
    weekday_str = weekdays[now.weekday()]
    return f"Bây giờ là {now.hour} giờ {now.minute:02d} phút, {weekday_str}, ngày {now.day} tháng {now.month} năm {now.year}."

def ask_gemini_ai(prompt):
    """
    Truy vấn câu hỏi trực tiếp qua Gemini API siêu nhanh (~1 giây, phản hồi bằng giọng nói).
    Không mở cửa sổ dòng lệnh terminal!
    """
    if not GEMINI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    system_instruction = (
        "Bạn là Alex, một trợ lý ảo thông minh bằng tiếng Việt trên Windows. "
        "Hãy trả lời người dùng một cách thân thiện, chính xác, cực kỳ ngắn gọn và súc tích (1 đến 2 câu ngắn) "
        "để phát âm rõ ràng qua loa giọng nói, không dùng ký tự Markdown phức tạp."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }

    try:
        resp = requests.post(url, json=payload, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text = re.sub(r'[\*\#\_\[\]]', '', text).strip()
                return text
        else:
            # Dự phòng sang model flash-latest
            url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
            resp_fallback = requests.post(url_fallback, json=payload, timeout=8)
            if resp_fallback.status_code == 200:
                data = resp_fallback.json()
                text = data.get("candidates", [])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text = re.sub(r'[\*\#\_\[\]]', '', text).strip()
                return text
    except Exception as e:
        print(f" ⚠️ [GEMINI API ERROR]: {e}")
    return None

def ask_antigravity_headless(prompt):
    """Dự phòng: Chạy agy -p (print mode) ngầm không bật cửa sổ terminal"""
    try:
        res = subprocess.run(
            [AGY_PATH, "-p", f"Trả lời cực kỳ ngắn gọn 1 câu tiếng Việt: {prompt}"],
            capture_output=True,
            text=True,
            timeout=20,
            encoding="utf-8",
            errors="ignore"
        )
        output = res.stdout.strip()
        lines = [line.strip() for line in output.splitlines() if line.strip() and not line.startswith("Hey,") and "───" not in line]
        if lines:
            return lines[-1]
    except Exception:
        pass
    return None

def record_audio_interactive(max_duration=15, silence_timeout=1.2, initial_frames=None):
    """
    Thu âm tương tác thông minh:
    - Tự động đo độ ồn phòng (Adaptive Noise Floor)
    - Tự động ngắt khi phát hiện im lặng 1.2s sau khi nói
    - Hỗ trợ chốt lệnh bằng: chữ 'OVER', phím [Space], [Enter], hoặc bấm lại [Ctrl+Alt+Space]
    - Hỗ trợ hủy bằng: phím [Esc]
    """
    global is_recording
    stop_recording_event.clear()
    cancel_recording_event.clear()
    is_recording = True

    RATE = 16000
    CHUNK = 1024

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Đo độ ồn phòng trong 0.2s đầu tiên để thiết lập ngưỡng năng lượng chính xác
    ambient_samples = []
    for _ in range(3):
        chunk_data = stream.read(CHUNK, exception_on_overflow=False)
        ambient_samples.append(audioop.rms(chunk_data, 2))
    ambient_rms = int(sum(ambient_samples) / len(ambient_samples)) if ambient_samples else 100
    energy_threshold = max(200, int(ambient_rms * 1.6))

    frames = list(initial_frames) if initial_frames else []
    start_time = time.time()
    last_sound_time = start_time
    has_spoken = len(frames) > 0

    print("\n" + "=" * 65)
    print(" 🎙️ [MICRO ĐANG BẬT] Hãy nói yêu cầu của bạn...")
    print(f" (Độ ồn nền: {ambient_rms} | Ngưỡng kích hoạt: {energy_threshold})")
    print(" 💡 MẸO: Nói 'OVER' hoặc bấm [SPACE] / [ENTER] để gửi lệnh ngay.")
    print(" 💡 Bấm [ESC] để hủy bỏ.")
    print("=" * 65)

    try:
        while True:
            if cancel_recording_event.is_set():
                print("\n 🚫 [ĐÃ HỦY]: Bạn đã bấm ESC để hủy lệnh.")
                play_beep("cancel")
                return None

            if stop_recording_event.is_set():
                print("\n ⏹️ [CHỐT LỆNH TỨC THÌ]: Nhận phím bấm dừng thu âm!")
                play_beep("stop")
                break

            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            rms = audioop.rms(data, 2)
            now = time.time()
            if rms > energy_threshold:
                has_spoken = True
                last_sound_time = now
            elif has_spoken and (now - last_sound_time > silence_timeout):
                print("\n 🛑 [TỰ ĐỘNG NGẮT]: Đã phát hiện dứt câu.")
                break

            if now - start_time > max_duration:
                print("\n ⏱️ [HẾT GIỜ]: Đã đạt giới hạn thời gian thu âm tối đa.")
                break
    finally:
        is_recording = False
        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception:
            pass

    raw_audio = b"".join(frames)
    if len(raw_audio) < RATE * 0.4:
        return None
    return sr.AudioData(raw_audio, RATE, 2)

def execute_command_smart_router(command):
    """
    BỘ ĐIỀU PHỐI LỆNH THÔNG MINH (SMART ROUTER):
    1. Tác vụ nhanh trên Windows (Mở web, phần mềm, giờ, pin, âm lượng) -> Xử lý tức thì 0s, không mở Antigravity.
    2. Câu hỏi thông tin / Hỏi đáp AI -> Hỏi Gemini AI siêu nhanh (~1s), trả lời bằng giọng nói và in ra màn hình.
    3. Lập trình / Tác vụ kỹ thuật -> CHỈ mở cửa sổ Antigravity CLI khi người dùng yêu cầu rõ ràng.
    """
    command_clean, has_over = strip_over_termination(command)
    if has_over:
        print(" 📌 [TỪ KHÓA CHỐT]: Phát hiện từ 'OVER' chốt câu!")
        play_beep("stop")

    if not command_clean:
        speak("Alex chưa nghe rõ nội dung câu lệnh.")
        return

    cmd_lower = command_clean.lower().strip()
    print(f"\n" + "=" * 65)
    print(f" ⚙️ [ĐANG XỬ LÝ LỆNH]: \"{command_clean}\"")
    print("=" * 65)

    # -------------------------------------------------------------
    # NHÓM 1: TÁC VỤ HỆ THỐNG CỤC BỘ (LOCAL FAST ACTIONS) - PHẢN HỒI TỨC THÌ
    # -------------------------------------------------------------

    # 1.1 Xem giờ / Ngày tháng
    if any(k in cmd_lower for k in ["mấy giờ", "thời gian", "bây giờ là mấy giờ", "ngày mấy", "ngày bao nhiêu", "hôm nay thứ mấy"]):
        info = get_date_time_info()
        speak(info)
        return

    # 1.2 Kiểm tra pin
    if any(k in cmd_lower for k in ["kiểm tra pin", "pin còn bao nhiêu", "mức pin", "thời lượng pin", "pin máy tính"]):
        info = get_battery_info()
        speak(info)
        return

    # 1.3 Điều khiển âm lượng
    if any(k in cmd_lower for k in ["tăng âm lượng", "tăng tiếng", "bật to lên", "cho to lên"]):
        for _ in range(5):
            keyboard.send("volume up")
        speak("Đã tăng âm lượng.")
        return

    if any(k in cmd_lower for k in ["giảm âm lượng", "giảm tiếng", "cho nhỏ lại", "nhỏ bớt"]):
        for _ in range(5):
            keyboard.send("volume down")
        speak("Đã giảm âm lượng.")
        return

    if any(k in cmd_lower for k in ["tắt tiếng", "im lặng", "mute", "bật lại tiếng", "bật tiếng"]):
        keyboard.send("volume mute")
        speak("Đã chuyển trạng thái âm thanh.")
        return

    # 1.4 Mở các trang web phổ biến
    if any(k in cmd_lower for k in ["mở youtube", "bật youtube", "vào youtube"]):
        webbrowser.open("https://www.youtube.com")
        speak("Đã mở YouTube cho bạn.")
        return

    if any(k in cmd_lower for k in ["mở facebook", "bật facebook", "vào facebook"]):
        webbrowser.open("https://www.facebook.com")
        speak("Đã mở Facebook cho bạn.")
        return

    if any(k in cmd_lower for k in ["mở google", "bật google", "vào google"]):
        webbrowser.open("https://www.google.com")
        speak("Đã mở trang Google.")
        return

    # 1.5 Mở ứng dụng Windows
    if any(k in cmd_lower for k in ["mở chrome", "bật chrome", "mở trình duyệt"]):
        os.system("start chrome")
        speak("Đã mở trình duyệt Chrome.")
        return

    if any(k in cmd_lower for k in ["mở notepad", "bật notepad", "mở ghi chú"]):
        os.system("start notepad")
        speak("Đã mở Notepad.")
        return

    if any(k in cmd_lower for k in ["mở máy tính", "calculator", "máy tính bỏ túi"]):
        os.system("start calc")
        speak("Đã mở ứng dụng máy tính.")
        return

    if any(k in cmd_lower for k in ["mở thư mục", "mở explorer", "mở ổ đĩa", "quản lý tệp"]):
        os.system("start explorer")
        speak("Đã mở quản lý tệp Windows.")
        return

    # 1.6 Khóa máy tính
    if any(k in cmd_lower for k in ["khóa máy", "khóa màn hình", "lock máy"]):
        speak("Đã khóa máy tính.")
        time.sleep(0.5)
        ctypes.windll.user32.LockWorkStation()
        return

    # 1.7 Tìm kiếm web trên Google
    search_match = re.match(r"^(?:tìm kiếm|tra cứu|tìm trên mạng|google)\s+(?:cho tôi|cho mình|về|)?\s*(.+)$", cmd_lower)
    if search_match:
        query = search_match.group(1).strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
            speak(f"Đang tìm kiếm {query} trên Google.")
            return

    # -------------------------------------------------------------
    # NHÓM 2: LẬP TRÌNH & KỸ THUẬT VỚI ANTIGRAVITY (CHỈ KHI YÊU CẦU CỤ THỂ)
    # -------------------------------------------------------------
    antigravity_triggers = [
        "antigravity", "mở agy", "bật agy", "chạy agy",
        "mở cli", "lập trình", "viết code", "sửa code", "fix bug",
        "tạo dự án", "refactor code", "viết script"
    ]
    if any(trigger in cmd_lower for trigger in antigravity_triggers):
        print(f"\n [KÍCH HOẠT ANTIGRAVITY CLI]: {command_clean}")
        speak("Đang mở Antigravity CLI để hỗ trợ bạn lập trình.")
        try:
            agy_cmd = f'"{AGY_PATH}" -i "{command_clean}"'
            subprocess.Popen(f'start "Antigravity CLI - Alex" cmd.exe /k {agy_cmd}', shell=True)
            print(" [THÀNH CÔNG]: Đã mở cửa sổ Antigravity CLI!")
        except Exception as e:
            print(f" [LỖI MỞ AGY]: {e}")
            speak("Có lỗi khi khởi chạy Antigravity CLI.")
        return

    # -------------------------------------------------------------
    # NHÓM 3: HỎI ĐÁP THÔNG TIN VỚI GEMINI AI (SIÊU NHANH, KHÔNG MỞ TERMINAL)
    # -------------------------------------------------------------
    print(" 🤖 [AI CHAT]: Đang truy vấn trí tuệ nhân tạo Gemini...")
    ai_answer = ask_gemini_ai(command_clean)
    if not ai_answer:
        # Fallback headless agy nếu không có internet hoặc API lỗi
        ai_answer = ask_antigravity_headless(command_clean)

    if ai_answer:
        print(f" 💡 [CÂU TRẢ LỜI CỦA ALEX]:\n{ai_answer}\n")
        speak(ai_answer)
    else:
        speak("Alex đã ghi nhận yêu cầu của bạn nhưng hiện tại chưa nhận được phản hồi từ AI.")

def handle_user_interaction(recognizer, initial_frames=None):
    """Quản lý phiên thu âm tương tác và chuyển hóa giọng nói thành hành động"""
    audio_data = record_audio_interactive(max_duration=15, silence_timeout=1.2, initial_frames=initial_frames)
    if not audio_data:
        print(" ℹ️ [THÔNG BÁO]: Không nhận được âm thanh nào.")
        return

    print(" 🔄 [ĐANG DỊCH]: Đang phân tích giọng nói của bạn...")
    try:
        command = recognizer.recognize_google(audio_data, language="vi-VN")
        print(f" 🎯 [BẠN NÓI]: \"{command}\"")
        play_beep("success")
        
        # Thực thi lệnh qua Smart Router
        execute_command_smart_router(command)
        
    except sr.UnknownValueError:
        print(" ❓ [KHÔNG RÕ]: Không nhận diện được âm thanh rõ ràng.")
        play_beep("error")
        speak("Alex chưa nghe rõ, bạn có thể nói lại được không?")
    except Exception as e:
        print(f" ⚠️ [LỖI DỊCH]: {e}")

def on_hotkey_pressed(recognizer):
    """Xử lý khi bấm phím tắt toàn cục Ctrl + Alt + Space"""
    global is_processing, is_recording
    if is_recording:
        stop_recording_event.set()
        return

    if is_processing:
        print(" ⏳ [BẬN]: Alex đang thực hiện một lệnh khác, vui lòng chờ trong giây lát...")
        return

    with lock:
        is_processing = True

    try:
        print(f"\n ⌨️ [HOTKEY KÍCH HOẠT]: Đã nhấn {GLOBAL_HOTKEY.upper()}!")
        play_beep("ready")
        speak("Dạ, Alex đang nghe!")
        handle_user_interaction(recognizer)
    finally:
        # Thời gian cooldown để loa tắt hẳn và micro ổn định lại
        time.sleep(1.0)
        with lock:
            is_processing = False

def on_global_key_event(e):
    """Bắt các phím Space / Enter / Esc khi micro đang thu âm để dừng/hủy ngay"""
    global is_recording
    if not is_recording:
        return

    if e.event_type == keyboard.KEY_DOWN:
        if e.name in ["space", "enter"]:
            stop_recording_event.set()
        elif e.name == "esc":
            cancel_recording_event.set()

def continuous_wake_word_loop(recognizer):
    """
    Vòng lặp lắng nghe liên tục bằng mô hình AI On-device (openWakeWord):
    - ĐỘ TIN CẬY CAO: Ngưỡng chuẩn 0.45 + Xác thực 2 khung hình liên tiếp để triệt tiêu kích hoạt nhầm
    - RESET STATE: Xóa sạch bộ nhớ đệm âm học sau mỗi lần kích hoạt
    - COOLDOWN GUARD: Tuyệt đối không nghe lại khi lệnh trước chưa hoàn thành
    """
    global is_processing, is_recording
    
    print(" 🚀 [ALEX AI]: Đang nạp mô hình âm học On-device Neural Wake Word...")
    try:
        owwModel = Model(wakeword_models=["alexa"], inference_framework="onnx")
        print(" ✅ [ALEX AI]: Mô hình On-Device đã sẵn sàng! Độ trễ phản hồi ~0.15s.")
    except Exception as e:
        print(f" ❌ [LỖI TẢI MÔ HÌNH]: {e}")
        return

    CHUNK_SAMPLES = 1280  # 80ms tại 16000Hz (chuẩn mô hình openWakeWord)
    RATE = 16000
    PRE_ROLL_CHUNKS = 6   # Lưu trữ ~0.48s âm thanh đệm
    ring_buffer = collections.deque(maxlen=PRE_ROLL_CHUNKS)

    p = pyaudio.PyAudio()
    consecutive_hits = 0
    
    while True:
        if is_processing or is_recording:
            time.sleep(0.3)
            continue

        try:
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK_SAMPLES)
        except Exception:
            time.sleep(1)
            continue

        # Xóa sạch bộ nhớ đệm trước khi mở lại micro
        owwModel.reset()
        ring_buffer.clear()
        consecutive_hits = 0
        
        # Đọc bỏ qua 2 chunk đầu tiên để tránh xung kích âm thanh khi mở stream
        try:
            for _ in range(2):
                stream.read(CHUNK_SAMPLES, exception_on_overflow=False)
        except Exception:
            pass

        print(" 🟢 [ALEX ONLINE]: Đang lắng nghe 'Hey Alex' hoặc 'Alex'...")

        try:
            while not (is_processing or is_recording):
                audio_bytes = stream.read(CHUNK_SAMPLES, exception_on_overflow=False)
                ring_buffer.append(audio_bytes)
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

                prediction = owwModel.predict(audio_np)
                score = prediction.get("alexa", 0.0)

                # Kiểm tra điều kiện kích hoạt:
                # 1. Hoặc đạt độ tin cậy rất cao (>= 0.55) trong 1 frame
                # 2. Hoặc đạt mức >= 0.42 trong 2 frame liên tiếp (~160ms)
                is_wake = False
                if score >= HIGH_CONFIDENCE_THRESHOLD:
                    is_wake = True
                elif score >= WAKE_THRESHOLD:
                    consecutive_hits += 1
                    if consecutive_hits >= 2:
                        is_wake = True
                else:
                    consecutive_hits = 0

                if is_wake:
                    print(f"\n ⚡ [WAKE WORD DETECTED]: Phát hiện 'ALEX'! (Độ tin cậy: {score:.2f})")
                    play_beep("wake")
                    
                    with lock:
                        is_processing = True

                    try:
                        stream.stop_stream()
                        stream.close()
                    except Exception:
                        pass

                    # Reset mô hình ngay lập tức để không lưu vết âm thanh
                    owwModel.reset()
                    pre_roll_data = list(ring_buffer)
                    ring_buffer.clear()
                    consecutive_hits = 0

                    try:
                        speak("Dạ, Alex đang nghe!")
                        handle_user_interaction(recognizer)
                    finally:
                        # Cooldown 1.2s để âm thanh loa phát xong tiêu tán hoàn toàn trong phòng
                        time.sleep(1.2)
                        owwModel.reset()
                        ring_buffer.clear()
                        with lock:
                            is_processing = False
                    
                    break
        except Exception as e:
            pass
        finally:
            try:
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
            except Exception:
                pass
            time.sleep(0.3)

def main():
    print("""
  ╔════════════════════════════════════════════════════════════════╗
  ║       TRỢ LÝ ẢO ALEX V4.0 (SMART ROUTER & ON-DEVICE AI)        ║
  ╚════════════════════════════════════════════════════════════════╝
  [*] NÂNG CẤP V4.0:
      - SMART ROUTER: Mở web, ứng dụng, kiểm tra giờ, pin, âm lượng tức thì.
      - GEMINI AI VOICE: Trả lời kiến thức bằng giọng nói (~1s), KHÔNG mở CLI.
      - ANTIGRAVITY DEV: Chỉ mở cửa sổ dòng lệnh khi bạn muốn code/lập trình.
      - CHỐNG KÍCH HOẠT NHẦM: Dual-frame verification + Auto Model Reset.
      - CHỐNG LẮNG NGHE ĐÈ: Khóa phiên hoàn toàn cho đến khi lệnh trước kết thúc.
  [*] 2 CÁCH GỌI ALEX:
      1. Nói: 'Hey Alex' hoặc 'Alex'
      2. Phím tắt: [ Ctrl + Alt + Space ]
  [*] CÁCH CHỐT LỆNH:
      - Tự động ngắt khi dừng nói 1.2s.
      - Nói 'OVER' ở cuối câu (phòng ồn).
      - Bấm [Space] / [Enter] để gửi ngay | Bấm [Esc] để hủy.
  ------------------------------------------------------------------
    """)

    recognizer = sr.Recognizer()

    # Lắng nghe phím Space / Enter / Esc toàn cục khi thu âm
    keyboard.hook(on_global_key_event)

    # Đăng ký Hotkey Ctrl + Alt + Space
    try:
        keyboard.add_hotkey(GLOBAL_HOTKEY, lambda: on_hotkey_pressed(recognizer))
        print(f" [PHÍM TẮT]: Đã kích hoạt Hotkey -> [{GLOBAL_HOTKEY.upper()}]")
    except Exception as e:
        print(f" [LƯU Ý]: Không thể đăng ký Hotkey: {e}")

    # Chạy vòng lặp Continuous Wake Word Engine ở thread nền
    wake_thread = threading.Thread(
        target=continuous_wake_word_loop,
        args=(recognizer,),
        daemon=True,
    )
    wake_thread.start()

    # Báo hiệu âm thanh và giọng nói khởi động thành công
    try:
        play_beep("success")
        speak("Trợ lý Alex đã sẵn sàng phục vụ bạn!")
    except Exception:
        pass

    print("\n [ALEX HOÀN TẤT]: Đang chạy ngầm và lắng nghe...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n [ĐÃ DỪNG] Đã tắt trợ lý Alex.")

if __name__ == "__main__":
    main()
