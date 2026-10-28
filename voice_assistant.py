import os
import sys

# Cấu hình UTF-8 toàn diện cho console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Đảm bảo thư mục gốc của Alex luôn nằm đầu sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import re
import time
import shutil
import collections
import threading
import audioop
import winsound
import numpy as np
import pyaudio
import speech_recognition as sr
from gtts import gTTS
import pygame
try:
    pygame.mixer.init()
except Exception as e:
    print(f" [LƯU Ý]: pygame.mixer chưa thể khởi tạo ngay: {e}")

import keyboard
from openwakeword.model import Model

# Import các module kiến trúc mới
import alex_actions
import alex_brain
from alex_hud import AlexHUD
GLOBAL_HOTKEY = "ctrl+alt+space"

# Tự động tìm đường dẫn Antigravity CLI (agy)
def get_antigravity_executable():
    agy_on_path = shutil.which("agy") or shutil.which("agy.exe")
    if agy_on_path:
        return agy_on_path
    default_gemini_path = os.path.expanduser(r"~/.gemini/bin/agy.exe")
    if os.path.exists(default_gemini_path):
        return default_gemini_path
    return "agy"

AGY_PATH = get_antigravity_executable()

# Ngưỡng kích hoạt mô hình Wake Word On-device (Tối ưu cho tiếng Việt)
WAKE_THRESHOLD = 0.28
PEAK_CONFIDENCE_THRESHOLD = 0.40

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

# Khởi tạo Floating HUD giao diện nổi
hud = AlexHUD()

def strip_over_termination(text):
    """Kiểm tra và cắt bỏ từ khóa kết thúc câu 'over' (hoặc 'âu vơ', 'ô vơ') ở cuối câu"""
    if not text:
        return text, False
    match = OVER_TERMINATION_PATTERN.search(text)
    if match:
        cleaned_text = OVER_TERMINATION_PATTERN.sub("", text).strip()
        return cleaned_text, True
    return text.strip(), False

def speak(text, interruptible=True):
    """Phát âm giọng nói tiếng Việt tự nhiên (Hỗ trợ ngắt lời ngay lập tức nếu bấm Esc)"""
    if not text:
        return
    print(f" 🗣️ [ALEX NÓI]: {text}")
    temp_file = os.path.join(BASE_DIR, f"temp_{int(time.time() * 1000)}.mp3")
    try:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        tts = gTTS(text=text, lang="vi", slow=False)
        tts.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if interruptible and cancel_recording_event.is_set():
                pygame.mixer.music.stop()
                break
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
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

def record_audio_interactive(max_duration=15, silence_timeout=1.6, initial_frames=None):
    """
    Thu âm tương tác thông minh kết hợp hiển thị trạng thái lên Floating HUD:
    - Tự động đo độ ồn phòng (Adaptive Noise Floor)
    - Tự động ngắt khi phát hiện im lặng 1.6s sau khi nói
    - Hỗ trợ chốt lệnh bằng: từ 'OVER', phím [Space], [Enter], hoặc phím tắt
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

    # Đo độ ồn phòng trong 0.2s đầu tiên
    ambient_samples = []
    for _ in range(4):
        chunk_data = stream.read(CHUNK, exception_on_overflow=False)
        ambient_samples.append(audioop.rms(chunk_data, 2))
    ambient_rms = int(sum(ambient_samples) / len(ambient_samples)) if ambient_samples else 6
    energy_threshold = max(ambient_rms + 12, int(ambient_rms * 1.5))

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
                hud.show_error("Đã hủy lệnh", "Bạn đã nhấn phím Esc", auto_hide_ms=1800)
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

def handle_user_interaction(recognizer, initial_frames=None):
    """Quản lý trọn vẹn luồng tương tác của người dùng và cập nhật giao diện HUD"""
    hud.show("🎙️", "Alex đang nghe...", "Mẹo: Nói 'OVER' hoặc bấm Space để gửi")
    
    audio_data = record_audio_interactive(max_duration=15, silence_timeout=1.8, initial_frames=initial_frames)
    if not audio_data:
        print(" ℹ️ [THÔNG BÁO]: Không nhận được âm thanh nào.")
        hud.hide()
        return

    print(" 🔄 [ĐANG DỊCH]: Đang phân tích giọng nói của bạn...")
    hud.update_text("Đang nhận diện giọng nói...", "Vui lòng chờ trong giây lát")

    try:
        command = recognizer.recognize_google(audio_data, language="vi-VN")
        command, has_over = strip_over_termination(command)
        print(f" 🎯 [BẠN NÓI]: \"{command}\"")
        play_beep("success")
        
        hud.update_text(f"\"{command}\"", "Đang xử lý yêu cầu...")

        # Xử lý lệnh qua Alex Brain Router
        result = alex_brain.process_command(command, agy_path=AGY_PATH)
        
        # KIỂM TRA NẾU LỆNH YÊU CẦU LÀM RÕ ĐA LƯỢT (MULTI-TURN CLARIFICATION SESSION)
        if result.get("type") == "clarify":
            # 1. Phát âm câu hỏi của Alex: "Bạn muốn nghe 'Sóng Gió' trên YouTube, Spotify hay Zing MP3?"
            clarify_speech = result.get("speech", "Bạn muốn chọn phương án nào?")
            hud.show("❓", result.get("title", "Làm rõ yêu cầu"), result.get("hud_sub", "Đang chờ bạn trả lời..."))
            speak(clarify_speech)

            # 2. Phát âm bíp sẵn sàng và tự động mở micro lắng nghe (không cần gọi lại 'Hey Alex')
            play_beep("ready")
            print("\n" + "=" * 65)
            print(" 👂 [ALEX CHỜ CÂU TRẢ LỜI]: Đang lắng nghe lựa chọn của bạn...")
            print(" (Nói: 'YouTube', 'Spotify' hoặc 'Zing MP3')")
            print("=" * 65)
            hud.update_text("Alex đang nghe lựa chọn...", "Nói: YouTube / Spotify / Zing MP3...")

            followup_audio = record_audio_interactive(max_duration=8, silence_timeout=1.4)
            followup_text = ""
            if followup_audio:
                try:
                    followup_text = recognizer.recognize_google(followup_audio, language="vi-VN")
                    followup_text, _ = strip_over_termination(followup_text)
                    print(f" 🎯 [BẠN TRẢ LỜI]: \"{followup_text}\"")
                    play_beep("success")
                except Exception:
                    pass

            # 3. Phân giải lựa chọn của người dùng hoặc fallback an toàn
            if not followup_text:
                print(" ℹ️ [TỰ ĐỘNG CHỌN]: Không nhận được câu trả lời rõ ràng, Alex sẽ mở trên YouTube.")
                followup_text = "youtube"

            result = alex_brain.resolve_clarification(result, followup_text)

        # Cập nhật kết quả lên Floating HUD
        hud.show_success(
            title=result.get("title", "Đã thực hiện"),
            subtitle=result.get("hud_sub", ""),
            auto_hide_ms=2800
        )

        # Phát âm kết quả qua loa (nếu có lời thoại)
        speech_text = result.get("speech", "")
        if speech_text:
            speak(speech_text)

    except sr.UnknownValueError:
        print(" ❓ [KHÔNG RÕ]: Không nhận diện được âm thanh rõ ràng.")
        play_beep("error")
        hud.show_error("Alex chưa nghe rõ", "Bấm Ctrl+Alt+Space hoặc gọi lại 'Alex'", auto_hide_ms=2000)
    except Exception as e:
        print(f" ⚠️ [LỖI DỊCH]: {e}")
        hud.show_error("Có lỗi xảy ra", str(e), auto_hide_ms=2500)

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
        handle_user_interaction(recognizer)
    finally:
        time.sleep(1.0)
        with lock:
            is_processing = False

def on_global_key_event(e):
    """Bắt các phím Space / Enter / Esc khi micro đang thu âm hoặc phát âm thanh"""
    global is_recording
    if e.event_type == keyboard.KEY_DOWN:
        if e.name == "esc":
            cancel_recording_event.set()
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            hud.hide()
        elif is_recording and e.name in ["space", "enter"]:
            stop_recording_event.set()

def continuous_wake_word_loop(recognizer):
    """
    Vòng lặp lắng nghe liên tục bằng mô hình AI On-device (openWakeWord):
    - DUAL-FRAME VERIFICATION: Ngưỡng 0.45 + 2 khung hình liên tiếp để triệt tiêu kích hoạt nhầm
    - RESET STATE: Xóa sạch bộ đệm âm học ngay khi kích hoạt
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
    PRE_ROLL_CHUNKS = 6
    ring_buffer = collections.deque(maxlen=PRE_ROLL_CHUNKS)

    p = pyaudio.PyAudio()
    consecutive_hits = 0
    recent_scores = collections.deque(maxlen=5)
    
    while True:
        if is_processing or is_recording:
            time.sleep(0.3)
            continue

        try:
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK_SAMPLES)
        except Exception:
            time.sleep(1)
            continue

        owwModel.reset()
        ring_buffer.clear()
        recent_scores.clear()
        consecutive_hits = 0
        
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

                rms = audioop.rms(audio_bytes, 2)
                prediction = owwModel.predict(audio_np)
                score = prediction.get("alexa", 0.0)
                recent_scores.append(score)

                is_wake = False
                # Bỏ qua khi mic tắt tiếng hoàn toàn
                if rms >= 2:
                    if score >= WAKE_THRESHOLD:
                        consecutive_hits += 1
                        if consecutive_hits >= 2:
                            is_wake = True
                    else:
                        consecutive_hits = 0

                    if not is_wake and len(recent_scores) >= 3:
                        sustained_hits = sum(1 for s in recent_scores if s >= 0.22)
                        peak_score = max(recent_scores)
                        if sustained_hits >= 2 and peak_score >= PEAK_CONFIDENCE_THRESHOLD:
                            is_wake = True
                else:
                    consecutive_hits = 0

                if is_wake:
                    print(f"\n ⚡ [WAKE WORD DETECTED]: Phát hiện 'ALEX'! (Độ tin cậy: {score:.2f}, RMS: {rms})")
                    play_beep("wake")
                    
                    with lock:
                        is_processing = True

                    try:
                        stream.stop_stream()
                        stream.close()
                    except Exception:
                        pass

                    owwModel.reset()
                    ring_buffer.clear()
                    recent_scores.clear()
                    consecutive_hits = 0

                    try:
                        handle_user_interaction(recognizer)
                    finally:
                        # Thời gian đệm 1.5s chống dội âm và reset sạch mô hình nhận diện
                        time.sleep(1.5)
                        owwModel.reset()
                        ring_buffer.clear()
                        recent_scores.clear()
                        with lock:
                            is_processing = False
                    
                    break
        except Exception:
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
  ║       TRỢ LÝ ẢO ALEX V4.5 (FLOATING HUD & VOICE ACTIONS)       ║
  ╚════════════════════════════════════════════════════════════════╝
  [*] CÁC ĐIỂM NÂNG CẤP ĐỘT PHÁ:
      - FLOATING HUD: Giao diện viên thuốc nổi trong suốt (Topmost Pill).
      - VOICE DICTATION: Gõ văn bản tiếng Việt trực tiếp vào Word, Zalo, Chat.
      - WINDOWS CONTROLS: Độ sáng, âm lượng, chụp màn hình, hiện Desktop.
      - GEMINI AI VOICE: Hỏi đáp kiến thức tức thì, không bật cửa sổ dòng lệnh.
      - ANTIGRAVITY DEV: Chỉ mở Terminal khi người dùng muốn lập trình.
      - CHỐNG KÍCH HOẠT NHẦM & CHỐNG NGHE ĐÈ: Khóa phiên chặt chẽ.
  [*] CÁCH SỬ DỤNG:
      1. Gọi: 'Hey Alex' hoặc 'Alex'
      2. Phím tắt: [ Ctrl + Alt + Space ]
      3. Chốt lệnh: Nói 'OVER' hoặc bấm [Space] / [Enter]
      4. Hủy lệnh / Ngắt lời: Bấm [Esc]
  ------------------------------------------------------------------
    """)

    recognizer = sr.Recognizer()

    # Lắng nghe phím Space / Enter / Esc toàn cục
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

    # Báo hiệu khởi động
    try:
        play_beep("success")
        hud.show_success("Trợ lý Alex đã sẵn sàng!", "Bấm Ctrl+Alt+Space hoặc gọi 'Hey Alex'", auto_hide_ms=2500)
    except Exception:
        pass

    print("\n [ALEX HOÀN TẤT]: Trợ lý đang chạy ngầm và sẵn sàng phục vụ...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n [ĐÃ DỪNG] Đã tắt trợ lý Alex.")

if __name__ == "__main__":
    main()
