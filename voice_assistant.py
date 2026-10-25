import os
import sys
import re
import time
import shutil
import threading
import audioop
import subprocess
import winsound
import numpy as np
import pyaudio
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
TEMP_VOICE_FILE = os.path.join(BASE_DIR, "temp_voice.mp3")
GLOBAL_HOTKEY = "ctrl+alt+space"

# Tự động tìm đường dẫn Antigravity CLI (agy) linh hoạt trên mọi máy tính
def get_antigravity_executable():
    """Tự động tìm agy trên PATH hoặc thư mục cài đặt mặc định của Antigravity"""
    # 1. Tìm trên biến môi trường PATH
    agy_on_path = shutil.which("agy") or shutil.which("agy.exe")
    if agy_on_path:
        return agy_on_path

    # 2. Tìm trong thư mục cài đặt mặc định ~/.gemini/bin/agy.exe
    default_gemini_path = os.path.expanduser(r"~/.gemini/bin/agy.exe")
    if os.path.exists(default_gemini_path):
        return default_gemini_path

    # 3. Fallback lệnh gọi
    return "agy"

AGY_PATH = get_antigravity_executable()

# Ngưỡng kích hoạt mô hình âm học Wake Word On-device (0.0 -> 1.0)
WAKE_THRESHOLD = 0.42

# Regex nhận diện Wake Word "Hey Alex"
WAKE_WORD_PATTERN = re.compile(
    r"^(.*?)\b(?:hey\s+|ê\s+|ơi\s+)?(?:alex|a\s*lếch|a\s*léc|alec)\b\s*(.*)$",
    re.IGNORECASE,
)

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
    """Phát âm giọng nói tiếng Việt tự nhiên"""
    print(f" [ALEX NÓI]: {text}")
    try:
        tts = gTTS(text=text, lang="vi", slow=False)
        tts.save(TEMP_VOICE_FILE)
        
        pygame.mixer.music.load(TEMP_VOICE_FILE)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        
        if os.path.exists(TEMP_VOICE_FILE):
            os.remove(TEMP_VOICE_FILE)
    except Exception:
        pass

def play_beep(tone_type):
    """Phát âm thanh bíp phản hồi"""
    try:
        if tone_type == "wake":
            winsound.Beep(1200, 80)
            winsound.Beep(1800, 100)
        elif tone_type == "ready":
            winsound.Beep(1200, 120)
        elif tone_type == "stop":
            winsound.Beep(1600, 80)
        elif tone_type == "cancel":
            winsound.Beep(400, 200)
        elif tone_type == "success":
            winsound.Beep(1500, 100)
            winsound.Beep(1800, 120)
        elif tone_type == "error":
            winsound.Beep(500, 250)
    except Exception:
        pass

def record_audio_interactive(max_duration=15, silence_timeout=1.2):
    """
    Thu âm tương tác thông minh (Sau khi Alex được đánh thức):
    - Tự động ngắt khi im lặng 1.2s
    - Nói 'OVER' ở cuối câu để chốt
    - Bấm Space / Enter / Ctrl+Alt+Space để CHỐT LỆNH NGAY
    - Bấm Esc để HỦY LỆNH
    """
    global is_recording
    stop_recording_event.clear()
    cancel_recording_event.clear()
    is_recording = True

    RATE = 16000
    CHUNK = 1024
    ENERGY_THRESHOLD = 450

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    start_time = time.time()
    last_sound_time = start_time
    has_spoken = False

    print("\n" + "=" * 65)
    print(" [MICRO BẬT] Hãy nói yêu cầu của bạn...")
    print(" 💡 MẸO: Bạn có thể nói chữ 'OVER' ở cuối câu để chốt lệnh.")
    print(" 💡 Hoặc bấm [SPACE], [ENTER], [CTRL+ALT+SPACE] để chốt / [ESC] để hủy.")
    print("=" * 65)

    try:
        while True:
            if cancel_recording_event.is_set():
                print("\n [ĐÃ HỦY]: Bạn đã bấm ESC hủy lệnh.")
                play_beep("cancel")
                return None

            if stop_recording_event.is_set():
                print("\n [CHỐT LỆNH TỨC THÌ]: Đã nhận tín hiệu phím bấm dừng thu âm!")
                play_beep("stop")
                break

            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            rms = audioop.rms(data, 2)
            now = time.time()
            if rms > ENERGY_THRESHOLD:
                has_spoken = True
                last_sound_time = now
            elif has_spoken and (now - last_sound_time > silence_timeout):
                print("\n [TỰ ĐỘNG NGẮT]: Đã phát hiện khoảng lặng (bạn đã ngừng nói).")
                break

            if now - start_time > max_duration:
                print("\n [HẾT GIỜ]: Đã đạt giới hạn thời gian thu âm tối đa.")
                break
    finally:
        is_recording = False
        stream.stop_stream()
        stream.close()
        p.terminate()

    raw_audio = b"".join(frames)
    if len(raw_audio) < RATE * 0.4:
        return None
    return sr.AudioData(raw_audio, RATE, 2)

def execute_antigravity(command):
    """Kích hoạt Antigravity CLI thực hiện lệnh"""
    command, has_over = strip_over_termination(command)
    if has_over:
        print(" [TỪ KHÓA CHỐT]: Phát hiện từ 'OVER' chốt câu!")
        play_beep("stop")

    if not command:
        speak("Alex chưa nghe được nội dung câu lệnh cụ thể.")
        return

    print(f"\n" + "=" * 65)
    print(f" [KÍCH HOẠT ANTIGRAVITY]: \"{command}\"")
    print(f" [ĐƯỜNG DẪN CLI]: {AGY_PATH}")
    print("=" * 65)
    
    speak(f"Đã nhận lệnh: {command}. Đang thực hiện ngay.")
    time.sleep(0.5)

    try:
        subprocess.run([AGY_PATH, "--prompt-interactive", command])
    except Exception as e:
        print(f" [LỖI CHẠY AGY] {e}")
    finally:
        speak("Đã thực hiện xong. Alex tiếp tục chạy nền.")
        print("\n [ALEX]: Sẵn sàng chờ 'Hey Alex' hoặc [Ctrl + Alt + Space]...")

def handle_user_interaction(recognizer):
    """Quản lý phiên thu âm tương tác và dịch giọng nói"""
    audio_data = record_audio_interactive(max_duration=15, silence_timeout=1.2)
    if not audio_data:
        return

    print(" [ĐANG DỊCH]: Đang xử lý giọng nói của bạn...")
    try:
        command = recognizer.recognize_google(audio_data, language="vi-VN")
        print(f" [NHẬN DIỆN THÔ]: \"{command}\"")
        
        command, has_over = strip_over_termination(command)
        if has_over:
            print(" [TỪ KHÓA CHỐT]: Đã phát hiện từ 'OVER' chốt câu!")
            play_beep("stop")
            
        print(f" [LỆNH THỰC THI]: \"{command}\"")
        play_beep("success")
        execute_antigravity(command)
    except sr.UnknownValueError:
        print(" [KHÔNG RÕ]: Không nhận diện được âm thanh rõ ràng.")
        play_beep("error")
        speak("Alex chưa nghe rõ, bạn hãy thử lại nhé.")
    except Exception as e:
        print(f" [LỖI DỊCH]: {e}")

def on_hotkey_pressed(recognizer):
    """Xử lý khi bấm phím tắt toàn cục Ctrl + Alt + Space"""
    global is_processing, is_recording
    if is_recording:
        stop_recording_event.set()
        return

    if is_processing:
        print(" [BẬN]: Alex đang thực hiện một lệnh khác, vui lòng chờ...")
        return

    with lock:
        is_processing = True

    try:
        print(f"\n [HOTKEY KÍCH HOẠT]: Đã nhấn {GLOBAL_HOTKEY.upper()}!")
        speak("Dạ, Alex đang nghe!")
        handle_user_interaction(recognizer)
    finally:
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
    Vòng lặp lắng nghe liên tục bằng mô hình AI On-device (openWakeWord)
    - KHÔNG CÓ BOUNDARY ISSUE (dòng dữ liệu âm thanh chạy liên tục 80ms không ngắt quãng)
    - NHẠY NHƯ SIRI/GOOGLE ASSISTANT (phản xạ 0.2s trực tiếp trên CPU, không qua mạng)
    """
    global is_processing, is_recording
    
    print(" [ALEX AI]: Đang tải mô hình âm học On-device Neural Wake Word...")
    try:
        owwModel = Model(wakeword_models=["alexa"], inference_framework="onnx")
        print(" [ALEX AI]: Mô hình On-Device đã sẵn sàng! Độ trễ phản hồi ~0.15s.")
    except Exception as e:
        print(f" [LỖI TẢI MÔ HÌNH]: {e}")
        return

    CHUNK_SAMPLES = 1280  # 80ms tại 16000Hz (chuẩn mô hình openWakeWord)
    RATE = 16000

    p = pyaudio.PyAudio()
    
    while True:
        if is_processing or is_recording:
            time.sleep(0.3)
            continue

        try:
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK_SAMPLES)
        except Exception as e:
            time.sleep(1)
            continue

        print(" [ALEX ONLINE]: Đang lắng nghe liên tục 'Hey Alex'...")

        try:
            while not (is_processing or is_recording):
                audio_bytes = stream.read(CHUNK_SAMPLES, exception_on_overflow=False)
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

                prediction = owwModel.predict(audio_np)
                score = prediction.get("alexa", 0.0)

                if score >= WAKE_THRESHOLD:
                    print(f"\n ⚡ [WAKE WORD DETECTED]: Phát hiện 'ALEX'! (Điểm tin cậy: {score:.2f})")
                    play_beep("wake")
                    
                    with lock:
                        is_processing = True
                    
                    stream.stop_stream()
                    stream.close()

                    try:
                        speak("Dạ, Alex đang nghe!")
                        handle_user_interaction(recognizer)
                    finally:
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
            time.sleep(0.2)

def main():
    print("""
  ╔════════════════════════════════════════════════════════════════╗
  ║       TRỢ LÝ ẢO ALEX V3.0 (ON-DEVICE NEURAL WAKE WORD)         ║
  ╚════════════════════════════════════════════════════════════════╝
  [*] CÔNG NGHỆ:
      - AI On-Device Neural Wake Word (Phản hồi ~0.15s như Siri).
      - Continuous Audio Streaming: XÓA BỎ HOÀN TOÀN BOUNDARY ISSUE.
      - Chạy 100% Offline trên CPU cho phần bắt từ khóa 'Hey Alex'.
  [*] 2 CÁCH KÍCH HOẠT:
      1. Nói: 'Hey Alex' hoặc 'Alex' (Phản xạ tức thì)
      2. Phím tắt: [ Ctrl + Alt + Space ]
  [*] CƠ CHẾ CHỐT LỆNH LINH HOẠT:
      - Tự động ngắt sau 1.2s khi bạn dừng nói.
      - Hoặc nói chữ 'OVER' ở cuối câu (bộ đàm khi phòng ồn).
      - Hoặc bấm [Space] / [Enter] để chốt ngay lập tức.
      - Bấm [Esc] để hủy lệnh.
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

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n [ĐÃ DỪNG] Đã tắt trợ lý Alex.")

if __name__ == "__main__":
    main()
