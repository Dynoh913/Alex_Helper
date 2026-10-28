# 🎙️ Alex Helper - Ultimate Windows Voice Assistant (V4.5)

> **Trợ lý ảo điều khiển máy tính bằng giọng nói hoàn chỉnh cho Windows 10/11 & Google Antigravity CLI.**  
> Sở hữu giao diện viên thuốc nổi trong suốt (**Floating Translucent HUD**), tính năng gõ văn bản tiếng Việt bằng giọng nói (**Voice Dictation**), điều khiển phần cứng/ứng dụng tức thì (0s latency), trả lời kiến thức bằng **Gemini AI**, và đánh thức Offline bằng mạng nơ-ron On-Device.

---

## ✨ Điểm Đột Phá Trên Phiên Bản V4.5

### 1. 🪟 Giao Diện Viên Thuốc Nổi (Floating HUD - Dynamic Pill)
- Thiết kế bo góc kính tối màu hiện đại (Windows 11 Dark Glass).
- Nổi mờ nhẹ nhàng ở mép trên màn hình khi bạn ra lệnh:
  - 🎙️ **Khi lắng nghe:** Hiển thị trạng thái micro và mẹo chốt lệnh.
  - 🔄 **Khi nhận diện:** Chữ của bạn xuất hiện ngay trên thanh HUD.
  - ✅ **Khi hoàn thành:** Chớp trạng thái thành công và tự động biến mất êm dịu sau 2.5s.
- **Chạy hoàn toàn ẩn:** Không còn bất kỳ cửa sổ dòng lệnh đen xì nào chiếm chỗ trên màn hình!

### 2. ✍️ Gõ Văn Bản Bằng Giọng Nói (Voice Dictation)
- Đặt con trỏ chuột vào bất cứ đâu: **Word, Zalo, Telegram, Messenger, Chrome, VS Code, Notepad...**
- Nói: *"Alex, gõ: Xin chào anh, em đã gửi báo cáo tài chính tháng 10 over"*
- Alex tự động chuyển thành chữ tiếng Việt chuẩn có dấu và **gõ thẳng vào ô nhập liệu** của bạn trong 0.1s!

### 3. ⚙️ Điều Khiển Máy Tính Tức Thì (Local Fast Actions - 0s Latency)
- **Hệ thống:**
  - *"Mấy giờ rồi"* / *"Hôm nay ngày mấy"*
  - *"Kiểm tra pin"* / *"Pin còn bao nhiêu"* (Đọc trực tiếp Windows API)
  - *"Tăng âm lượng"* / *"Giảm âm lượng"* / *"Tắt tiếng"*
  - *"Tăng độ sáng màn hình"* / *"Giảm độ sáng"*
  - *"Chụp màn hình"* (Kích hoạt nhanh Windows Snipping Tool)
  - *"Hiện desktop"* / *"Về màn hình chính"*
  - *"Đóng cửa sổ"* / *"Khóa máy tính"*
- **Mở Web & Phần Mềm:**
  - *"Mở YouTube"*, *"Mở Facebook"*, *"Mở Google"*, *"Mở Gmail"*, *"Mở Shopee"*
  - *"Mở Chrome"*, *"Mở Notepad"*, *"Mở máy tính"*, *"Mở Excel"*, *"Mở Word"*, *"Mở Zalo"*, *"Mở Spotify"*, *"Mở VS Code"*
- **Tìm kiếm:**
  - *"Tìm kiếm bài hát Cắt đôi nỗi sầu trên YouTube"*
  - *"Tìm kiếm địa điểm du lịch Đà Lạt trên Google"*

### 4. 🤖 Hỏi Đáp Thông Minh Với Gemini AI (Không Mở Terminal)
- Dành cho các câu hỏi tổng quát: thời tiết, dịch thuật, giải thích khái niệm, tính toán, hỏi đáp kiến thức...
- Trả lời ngắn gọn 1-2 câu tiếng Việt tự nhiên qua loa, hiển thị trên Floating HUD mà **không bật cửa sổ Antigravity**.

### 5. 💻 Chế Độ Lập Trình Antigravity CLI (Chuyên Sâu)
- **CHỈ** khi bạn nói rõ yêu cầu lập trình: *"Mở Antigravity"*, *"Lập trình game rắn săn mồi bằng Python"*, *"Sửa bug đoạn code này"*, Alex mới mở cửa sổ Antigravity CLI độc lập để pair-programming cùng bạn.

### 6. 🛡️ Chống Kích Hoạt Nhầm & Chống Nghe Đè (Anti-False & Anti-Overlap)
- Khóa phiên tuyệt đối: Tuyệt đối không nghe lại khi lệnh trước chưa hoàn thành hoặc khi loa đang phát lời thoại.
- Cơ chế đệm tản âm (Acoustic Cooldown 1.2s) + tự động reset bộ nhớ đệm âm học `openWakeWord`.
- Nhấn **`Esc`** bất kỳ lúc nào để ngắt lời Alex hoặc hủy lệnh ngay lập tức (Barge-in Mute).

---

## 🚀 Hướng Dẫn Sử Dụng

### Khởi chạy:
- **Chạy thường (Có bảng điều khiển):** Nhấp đúp vào `run.bat`
- **Chạy ngầm im lặng (Khuyên dùng):** Nhấp đúp vào `run_silent.vbs` (chỉ xuất hiện thanh Floating HUD khi bạn gọi Alex)
- **Tự khởi động cùng Windows:** Chạy `setup_startup.bat`

### 2 Cách Ra Lệnh:
1. **Gọi bằng giọng nói:** *"Hey Alex"* hoặc *"Alex"* (Mô hình AI Offline trên CPU)
2. **Phím tắt toàn cục:** **`Ctrl + Alt + Space`** ở bất cứ cửa sổ nào.

### Cách Chốt Câu Lệnh:
- Tự động ngắt khi bạn dừng nói $1.2\text{s}$.
- Nói từ khóa *"OVER"* ở cuối câu khi phòng ồn ào.
- Bấm **`Space`** hoặc **`Enter`** để gửi ngay.
- Bấm **`Esc`** để hủy bỏ hoặc ngắt lời Alex.

---

## 🗂️ Cấu Trúc Dự Án

```
Alex_Helper/
├── voice_assistant.py      # Bộ điều phối trung tâm & luồng âm học On-Device
├── alex_hud.py             # Giao diện viên thuốc nổi trong suốt (Floating HUD)
├── alex_actions.py         # Bộ máy điều khiển Windows Native, Apps & Dictation
├── alex_brain.py           # Bộ định tuyến ý định tự nhiên & Gemini AI Voice
├── test_alex_suite.py      # Bộ kiểm thử tự động 10/10 test case
├── download_models.py      # Tải mô hình âm học ONNX openWakeWord
├── install.bat             # Cài đặt tự động 1-click
├── run.bat                 # Khởi chạy có bảng điều khiển
├── run_silent.vbs          # Khởi chạy im lặng hoàn toàn trong nền
├── setup_startup.bat       # Đăng ký tự chạy cùng Windows
├── remove_startup.bat      # Gỡ bỏ tự chạy cùng Windows
├── requirements.txt        # Danh sách thư viện Python
└── README.md               # Tài liệu hướng dẫn sử dụng
```
