# 🎙️ Alex Helper - Antigravity Voice Assistant (V4.0)

> **Trợ lý ảo điều khiển bằng giọng nói thông minh cho Windows & Google Antigravity CLI.**  
> Hỗ trợ đánh thức tức thì bằng AI On-Device (*"Hey Alex"*), Phím tắt toàn cục (*Ctrl + Alt + Space*), cơ chế chốt lệnh kiểu bộ đàm (*"OVER"*), điều phối lệnh thông minh (Smart Router), trả lời kiến thức bằng AI siêu nhanh không mở cửa sổ, và phản hồi giọng nói tiếng Việt tự nhiên.

---

## ✨ Điểm Nổi Bật Trên Phiên Bản V4.0

- 🧠 **Điều Phối Lệnh Thông Minh (Smart Intent Router):**
  - **Tác vụ Windows nhanh (0s latency):** Mở YouTube, Google, Facebook, Chrome, Notepad, máy tính bỏ túi, kiểm tra giờ/ngày tháng, kiểm tra phần trăm pin laptop, tăng/giảm âm lượng, khóa máy tính... Tất cả xử lý tức thì, **tuyệt đối không bật cửa sổ Antigravity phiền phức**.
  - **Hỏi đáp kiến thức với Gemini AI:** Các câu hỏi thông thường, thời tiết, dịch thuật, giải thích khái niệm... được AI trả lời trực tiếp bằng giọng nói trong $\sim 1\text{s}$, không mở bất kỳ cửa sổ dòng lệnh nào!
  - **Chế độ Lập trình Antigravity (Chuyên sâu):** **CHỈ** mở cửa sổ tương tác Antigravity CLI khi bạn thực sự yêu cầu lập trình, viết code, sửa lỗi (bug), tạo dự án hoặc nói rõ *"mở Antigravity"*.

- 🛡️ **Khắc Phục Hoàn Toàn Lỗi Lắng Nghe Đè (Anti-Overlap) & Kích Hoạt Nhầm (Anti-False Wake):**
  - **Khóa phiên tuyệt đối:** Không bao giờ lắng nghe lại khi lệnh trước đó chưa hoàn thành hoặc khi loa máy tính đang phát lời thoại.
  - **Âm học On-Device chuẩn xác:** Sử dụng mô hình `openWakeWord` với thuật toán xác thực khung đôi (Dual-frame confidence verification) + tự động dọn sạch bộ nhớ đệm âm học (`Model.reset()`) sau mỗi lần kích hoạt, triệt tiêu kích hoạt nhầm do tiếng ồn môi trường.
  - **Đệm tản âm (Acoustic Cooldown):** Ngăn chặn micro tự thu âm thanh từ loa ngoài máy tính.

- ⚡ **On-Device Neural Wake Word (Phản xạ $\sim 0.15\text{s}$ như Siri/Google Assistant):**
  - Chạy mô hình mạng nơ-ron cục bộ trực tiếp trên CPU laptop, hoàn toàn Offline khi chờ từ khóa *"Hey Alex"*.
  - **Không có Boundary Issue:** Thu luồng âm thanh liên tục $80\text{ms}$ (Continuous Streaming).

- ⌨️ **Phím tắt toàn cục (Global Hotkey - `Ctrl + Alt + Space`):**
  - Kích hoạt micro ngay lập tức từ bất kỳ cửa sổ nào trên Windows.

- 📻 **Cơ chế chốt câu linh hoạt (Chống ồn tuyệt đối):**
  - **Tự động ngắt:** Sau $1.2\text{ giây}$ khi bạn ngừng nói.
  - **Từ khóa "OVER":** Nói chữ *"over"* ở cuối câu để chốt lệnh kiểu bộ đàm khi phòng ồn ào.
  - **Phím chốt lệnh:** Bấm **`Space`** hoặc **`Enter`** để ngắt thu âm và gửi lệnh tức thì.
  - **Phím hủy:** Bấm **`Esc`** để hủy bỏ lệnh.

---

## 🛠️ Yêu Cầu Hệ Thống

1. **Hệ điều hành:** Windows 10 / 11 (64-bit)
2. **Python:** 3.10 trở lên ([Tải tại python.org](https://www.python.org/))
3. **Google Antigravity CLI:** Đã cài đặt `agy` (tự động nhận diện)
4. **Gemini API Key (Tùy chọn):** Đặt trong biến môi trường `GEMINI_API_KEY` để kích hoạt hỏi đáp AI siêu tốc.

---

## 📦 Cài Đặt Nhanh (1-Click Installer)

### Bước 1: Clone kho lưu trữ
```bash
git clone https://github.com/Dynoh913/Alex_Helper.git
cd Alex_Helper
```

### Bước 2: Chạy cài đặt tự động
Nhấp đúp vào file **`install.bat`** (hoặc chạy trong terminal):
```cmd
install.bat
```

---

## 🚀 Hướng Dẫn Sử Dụng

Khởi chạy bằng cách nhấp đúp vào file **`run.bat`**.

### 1. Các câu lệnh phổ biến (Xử lý tức thì):
- *"Mấy giờ rồi"* / *"Hôm nay ngày mấy"*
- *"Kiểm tra pin"* / *"Pin còn bao nhiêu phần trăm"*
- *"Tăng âm lượng"* / *"Giảm âm lượng"* / *"Tắt tiếng"*
- *"Mở YouTube"* / *"Mở Facebook"* / *"Mở Google"* / *"Mở Chrome"*
- *"Mở Notepad"* / *"Mở máy tính"* / *"Mở quản lý tệp"*
- *"Tìm kiếm công thức làm bánh pizza trên Google"*
- *"Khóa máy"*

### 2. Các câu hỏi AI (Trả lời bằng giọng nói, không bật cửa sổ):
- *"Thủ đô của nước Pháp là gì?"*
- *"Giải thích trí tuệ nhân tạo một cách đơn giản"*
- *"1 dặm bằng bao nhiêu km?"*

### 3. Kích hoạt Antigravity CLI (Lập trình):
- *"Mở Antigravity"*
- *"Lập trình game rắn săn mồi bằng Python"*
- *"Viết script tự động hóa backup file"*

---

## 🗂️ Cấu Trúc Dự Án

```
Alex_Helper/
├── voice_assistant.py      # Mã nguồn chính của trợ lý Alex V4.0
├── download_models.py      # Tải mô hình âm học ONNX openWakeWord
├── install.bat             # Cài đặt tự động 1-click
├── run.bat                 # Khởi chạy trợ lý Alex
├── setup_startup.bat       # Đăng ký khởi động cùng Windows
├── remove_startup.bat      # Gỡ bỏ khởi động cùng Windows
├── requirements.txt        # Danh sách thư viện Python
└── README.md               # Tài liệu hướng dẫn sử dụng
```
