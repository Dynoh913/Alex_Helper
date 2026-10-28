# 🎙️ Alex Helper - Ultimate Windows Voice Assistant (V4.6 AI Reasoning)

> **Trợ lý ảo điều khiển máy tính bằng giọng nói thông minh hoàn chỉnh cho Windows 10/11 & Google Antigravity CLI.**  
> Sở hữu **Bộ Não Suy Luận Ngữ Nghĩa AI (Semantic Reasoning Engine)** dùng mô hình **Gemini AI**, giao diện viên thuốc nổi trong suốt (**Floating Translucent HUD**), tính năng gõ văn bản tiếng Việt bằng giọng nói (**Voice Dictation**), hội thoại làm rõ đa lượt (**Multi-turn Clarification**), điều khiển phần cứng/ứng dụng tức thì (0s latency), và đánh thức Offline bằng mạng nơ-ron On-Device.

---

## ✨ Điểm Đột Phá Trên Phiên Bản V4.6

### 1. 🧠 Bộ Não Suy Luận Ngữ Nghĩa AI (AI Semantic Reasoning Core)
- **Không còn fix cứng Regex**: Alex không còn dựa vào các câu lệnh dập khuôn thô sơ mà tự động suy luận ý đồ người dùng như một AI thực thụ.
- **Hiểu câu nói gián tiếp & cảm xúc:**
  - *"Chói mắt quá Alex ơi"* ➔ AI suy luận: Giảm độ sáng màn hình.
  - *"Loa bé quá cho to lên tí"* ➔ AI suy luận: Tăng âm lượng loa.
  - *"Tắt hết cửa sổ đi để tao làm việc"* ➔ AI suy luận: Ẩn tất cả cửa sổ về màn hình Desktop.
  - *"Máy tính còn bao nhiêu phần trăm điện"* ➔ AI suy luận: Đọc pin laptop (không bị nhầm với ứng dụng máy tính Calculator!).
  - *"Cho tớ nghe cái bài gì của Jack mà có hoa hải đường ấy"* ➔ AI suy luận: Tìm bài hát "Hoa Hải Đường" của Jack.
- **Hiển thị minh bạch:** In trực tiếp dòng `🧠 [AI SUY LUẬN]: ...` trên Terminal & HUD để người dùng theo dõi cách AI tư duy.
- **Kiến trúc 2 tầng (Two-Tier Hybrid Architecture):**
  - **Tier 1 (AI Reasoning Core):** Gemini AI phân tích ngữ nghĩa sâu, xử lý câu từ phức tạp (~1.5s).
  - **Tier 2 (Local Fast Heuristic):** Dự phòng cục bộ tự động 0s khi mất mạng hoặc mạng gián đoạn, đảm bảo trợ lý **không bao giờ ngừng hoạt động**.

### 2. 🎵 Hội Thoại Đa Lượt & Đa Nền Tảng (Multi-Turn Clarification)
- Khi bạn nói *"Bật bài Sóng Gió"*, Alex sẽ thông minh hỏi lại: *"Bạn muốn nghe bài Sóng Gió trên YouTube, Spotify hay Zing MP3?"*
- Micro tự động giữ mở trong 8s để bạn trả lời ngay mà **không cần gọi lại 'Alex'**.
- Người dùng có thể lưu nền tảng ưa thích làm mặc định: *"Đặt Spotify làm mặc định"*, *"Luôn hỏi nền tảng khi bật nhạc"*.
- Hỗ trợ phím điều khiển phát nhạc toàn hệ thống: Tạm dừng, tiếp tục, bài tiếp theo, bài trước đó.

### 3. ✨ Tiên Đoán & Sửa Lỗi Chính Tả / Phiên Âm (Predictive ASR Corrector)
- Tự động phát hiện và chuẩn hóa các lỗi nhận diện âm học ASR tiếng Việt:
  - *"Clickbuy bài sóng gió trên du túp"* ➔ Tự động sửa thành *"Bật bài Sóng Gió trên YouTube"*.
  - *"sờ po ti phai"*, *"dút túp"*, *"dinh mp3"* ➔ Tự động khớp về Spotify, YouTube, Zing MP3.

### 4. 🪟 Giao Diện Viên Thuốc Nổi (Floating HUD - Dynamic Pill)
- Thiết kế bo góc kính tối màu hiện đại (Windows 11 Dark Glass).
- Nổi mờ nhẹ nhàng ở mép trên màn hình khi bạn ra lệnh:
  - 🎙️ **Khi lắng nghe:** Hiển thị trạng thái micro và mẹo chốt lệnh.
  - 🔄 **Khi nhận diện:** Chữ của bạn xuất hiện ngay trên thanh HUD.
  - ✅ **Khi hoàn thành:** Chớp trạng thái thành công và tự động biến mất êm dịu sau 2.5s.
- **Chạy hoàn toàn ẩn:** Không còn bất kỳ cửa sổ dòng lệnh đen xì nào chiếm chỗ trên màn hình!

### 5. ✍️ Gõ Văn Bản Bằng Giọng Nói (Voice Dictation)
- Đặt con trỏ chuột vào bất cứ đâu: **Word, Zalo, Telegram, Messenger, Chrome, VS Code, Notepad...**
- Nói: *"Alex, gõ: Xin chào anh, em đã gửi báo cáo tài chính tháng 10 over"*
- Alex tự động chuyển thành chữ tiếng Việt chuẩn có dấu và **gõ thẳng vào ô nhập liệu** của bạn trong 0.1s!

### 6. ⚙️ Điều Khiển Máy Tính Tức Thì (Local Fast Actions - 0s Latency)
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

### 7. 🤖 Hỏi Đáp Thông Minh Với Gemini AI (Không Mở Terminal)
- Dành cho các câu hỏi tổng quát: thời tiết, dịch thuật, giải thích khái niệm, tính toán, hỏi đáp kiến thức...
- Trả lời ngắn gọn 1-2 câu tiếng Việt tự nhiên qua loa, hiển thị trên Floating HUD mà **không bật cửa sổ Antigravity**.

### 8. 💻 Chế Độ Lập Trình Antigravity CLI (Chuyên Sâu)
- **CHỈ** khi bạn nói rõ yêu cầu lập trình: *"Mở Antigravity"*, *"Lập trình game rắn săn mồi bằng Python"*, *"Sửa bug đoạn code này"*, Alex mới mở cửa sổ Antigravity CLI độc lập để pair-programming cùng bạn.

### 9. 🛡️ Chống Kích Hoạt Nhầm & Chống Nghe Đè (Anti-False & Anti-Overlap)
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
- Tự động ngắt khi bạn dừng nói $1.8\text{s}$ (chuẩn tự nhiên theo nhịp nói tiếng Việt).
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
├── test_alex_suite.py      # Bộ kiểm thử tự động 12/12 test case chuẩn xác
├── run.bat                 # Khởi động với cửa sổ Console
├── run_silent.vbs          # Khởi động ngầm hoàn toàn không hiện Console
└── setup_startup.bat       # Cài đặt tự khởi động cùng Windows
```
├── download_models.py      # Tải mô hình âm học ONNX openWakeWord
├── install.bat             # Cài đặt tự động 1-click
├── run.bat                 # Khởi chạy có bảng điều khiển
├── run_silent.vbs          # Khởi chạy im lặng hoàn toàn trong nền
├── setup_startup.bat       # Đăng ký tự chạy cùng Windows
├── remove_startup.bat      # Gỡ bỏ tự chạy cùng Windows
├── requirements.txt        # Danh sách thư viện Python
└── README.md               # Tài liệu hướng dẫn sử dụng
```
