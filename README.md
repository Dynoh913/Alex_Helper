# 🎙️ Alex Helper - Antigravity Voice Assistant

> **Trợ lý ảo điều khiển bằng giọng nói thông minh cho Google Antigravity CLI trên Windows.**  
> Hỗ trợ đánh thức tức thì bằng AI On-Device (*"Hey Alex"*), Phím tắt toàn cục (*Ctrl + Alt + Space*), cơ chế chốt lệnh kiểu bộ đàm (*"OVER"*), và phản hồi giọng nói tiếng Việt tự nhiên.

---

## ✨ Tính Năng Nổi Bật

- ⚡ **On-Device Neural Wake Word (Phản xạ $\sim 0.15\text{s}$ như Siri/Google Assistant):**
  - Chạy mô hình mạng nơ-ron âm học cục bộ (`openWakeWord` + `ONNX Runtime`) trực tiếp trên CPU laptop.
  - **Không có độ trễ đám mây**, hoàn toàn Offline khi chờ từ khóa *"Hey Alex"*.
  - **Xóa bỏ triệt để Boundary Issue:** Thu luồng âm thanh liên tục $80\text{ms}$ (Continuous Streaming), không bao giờ bị cắt xẻ đôi từ khóa.

- ⌨️ **Phím tắt toàn cục (Global Hotkey - `Ctrl + Alt + Space`):**
  - Kích hoạt micro ngay lập tức từ bất kỳ cửa sổ nào trên Windows (VS Code, trình duyệt, Word, Excel...).

- 📻 **Cơ chế chốt câu linh hoạt (Chống ồn tuyệt đối):**
  - **Tự động ngắt:** Sau $1.2\text{ giây}$ khi bạn ngừng nói.
  - **Từ khóa "OVER":** Nói chữ *"over"* ở cuối câu để chốt lệnh kiểu bộ đàm khi phòng ồn ào.
  - **Phím chốt lệnh:** Bấm **`Space`** hoặc **`Enter`** (hoặc bấm lại `Ctrl + Alt + Space`) để ngắt thu âm và gửi lệnh tức thì.
  - **Phím hủy:** Bấm **`Esc`** để hủy bỏ nếu đổi ý.

- 🗣️ **Phản hồi bằng giọng nói tiếng Việt (TTS):**
  - Phản hồi trạng thái, chào mừng và thông báo khi bắt đầu / hoàn thành nhiệm vụ.

- 🤖 **Tích hợp sâu Google Antigravity CLI (`agy`):**
  - Tự động chuyển câu lệnh giọng nói thành prompt và khởi chạy Antigravity CLI để tự động hóa tác vụ, code, sửa lỗi hoặc điều khiển hệ thống.

- 🚀 **Khởi động cùng Windows:**
  - Tùy chọn chạy ngầm thu nhỏ im lặng mỗi khi bạn bật máy tính.

---

## 🛠️ Yêu Cầu Hệ Thống

1. **Hệ điều hành:** Windows 10 / 11 (64-bit)
2. **Python:** 3.10 trở lên ([Tải tại python.org](https://www.python.org/) - nhớ tích chọn *Add Python to PATH* khi cài đặt)
3. **Google Antigravity CLI:** Đã cài đặt `agy`

---

## 📦 Cài Đặt Nhanh (1-Click Installer)

### Bước 1: Clone kho lưu trữ
```bash
git clone https://github.com/Dynoh913/Alex_Helper.git
cd Alex_Helper
```

### Bước 2: Chạy cài đặt tự động
Nhấp đúp vào file **`install.bat`** (hoặc chạy trong CMD/PowerShell):
```cmd
install.bat
```
Script sẽ tự động:
1. Tạo môi trường ảo Python (`.venv`).
2. Cài đặt các thư viện cần thiết (`SpeechRecognition`, `pyaudio`, `openwakeword`, `onnxruntime`, `gTTS`, `pygame`, `keyboard`...).
3. Tải các tệp mô hình âm học ONNX về máy.
4. Hỏi bạn có muốn kích hoạt tự động chạy cùng Windows hay không.

---

## 🚀 Hướng Dẫn Sử Dụng

Khởi chạy bằng cách nhấp đúp vào file **`run.bat`**. Bạn có 2 cách ra lệnh cho Alex:

### Cách 1: Gọi tên bằng giọng nói (*"Hey Alex"*) — Rảnh tay 100%
- **Nói liền câu:**  
  > *"Hey Alex, kiểm tra xem máy còn bao nhiêu phần trăm pin"*  
  > *(Hoặc: "Hey Alex, mở trình duyệt Chrome cho tôi **over**")*
- **Gọi tên trước, ra lệnh sau:**  
  1. Nói: *"Hey Alex"*
  2. Alex đáp: 🗣️ *"Dạ, Alex đang nghe!"*
  3. Bạn thong thả nói yêu cầu của mình.

### Cách 2: Dùng phím tắt (`Ctrl + Alt + Space`) — Khi phòng ồn ào
1. Bấm **`Ctrl + Alt + Space`** ở bất cứ đâu trên Windows.
2. Alex đáp: 🗣️ *"Dạ, Alex đang nghe!"*
3. Bạn nói câu lệnh.
4. Vừa dứt câu, bấm phím **`Enter`** hoặc **`Space`** để chốt gửi lệnh đi ngay lập tức!

---

## ⚙️ Tùy Biến Cấu Hình (Trong `voice_assistant.py`)

| Tham số | Mặc định | Mô tả |
| :--- | :--- | :--- |
| `WAKE_THRESHOLD` | `0.42` | Độ nhạy của từ khóa Alex ($0.0 \to 1.0$). Giảm xuống để nhạy hơn, tăng lên nếu muốn lọc tiếng ồn gắt hơn. |
| `GLOBAL_HOTKEY` | `"ctrl+alt+space"` | Tổ hợp phím kích hoạt toàn cục. |
| `AGY_PATH` | Tự động dò | Tự động tìm `agy.exe` trên `PATH` hoặc `~/.gemini/bin/agy.exe`. |

---

## 🗂️ Cấu Trúc Dự Án

```
Alex_Helper/
├── voice_assistant.py      # Mã nguồn chính của trợ lý Alex
├── download_models.py      # Tải mô hình âm học ONNX openWakeWord
├── install.bat             # File cài đặt tự động 1-Click
├── run.bat                 # File khởi chạy trợ lý
├── setup_startup.bat       # Kích hoạt tự khởi động cùng Windows
├── remove_startup.bat      # Hủy tự khởi động cùng Windows
├── requirements.txt        # Danh sách thư viện Python
├── .gitignore              # Bỏ qua môi trường ảo và file rác
└── README.md               # Tài liệu hướng dẫn sử dụng
```

---

## 📄 Bản Quyền

Dự án phát triển bởi **Dynoh913** phục vụ mục đích tự động hóa cá nhân và cộng đồng người dùng Google Antigravity.
Mọi đóng góp (Pull Requests / Issues) đều được chào đón!
