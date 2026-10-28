import tkinter as tk
import threading
import time

class AlexHUD:
    """
    Floating Translucent Pill Overlay (Heads-Up Display) cho trợ lý Alex:
    - Nổi trên cùng màn hình (Topmost, Frameless)
    - Thiết kế kính tối màu hiện đại (Windows 11 Dark Glass Style)
    - Hiển thị trực quan trạng thái, lời nói của người dùng và phản hồi của Alex
    - Hoàn toàn Thread-Safe
    """
    def __init__(self):
        self.root = None
        self.is_ready = False
        self.hide_timer = None
        self._thread = threading.Thread(target=self._run_ui, daemon=True)
        self._thread.start()
        
        # Chờ UI thread khởi tạo xong
        while not self.is_ready:
            time.sleep(0.05)

    def _run_ui(self):
        self.root = tk.Tk()
        self.root.title("Alex HUD")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.94)

        # Kích thước và căn giữa mép trên màn hình
        width = 460
        height = 74
        screen_w = self.root.winfo_screenwidth()
        x = (screen_w - width) // 2
        y = 28  # Cách mép trên 28px
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Khung chứa chính (Theme Dark Modern)
        self.bg_frame = tk.Frame(self.root, bg="#181825", highlightthickness=1, highlightbackground="#313244")
        self.bg_frame.pack(fill=tk.BOTH, expand=True)

        # Biểu tượng trạng thái
        self.icon_label = tk.Label(self.bg_frame, text="🎙️", font=("Segoe UI Emoji", 20), bg="#181825", fg="#89B4FA")
        self.icon_label.pack(side=tk.LEFT, padx=(16, 12))

        # Khung văn bản
        text_frame = tk.Frame(self.bg_frame, bg="#181825")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=12)

        self.title_label = tk.Label(text_frame, text="Alex đang nghe...", font=("Segoe UI", 11, "bold"), bg="#181825", fg="#CDD6F4", anchor="w")
        self.title_label.pack(fill=tk.X)

        self.sub_label = tk.Label(text_frame, text="Hãy nói yêu cầu của bạn...", font=("Segoe UI", 9), bg="#181825", fg="#A6ADC8", anchor="w")
        self.sub_label.pack(fill=tk.X)

        # Ban đầu ẩn đi
        self.root.withdraw()
        self.is_ready = True
        self.root.mainloop()

    def show(self, icon="🎙️", title="Alex đang nghe...", subtitle="Hãy nói yêu cầu của bạn..."):
        """Hiển thị HUD nổi lên màn hình (Thread-safe)"""
        if not self.root:
            return
        def _update():
            if self.hide_timer:
                self.root.after_cancel(self.hide_timer)
                self.hide_timer = None
            self.icon_label.config(text=icon)
            self.title_label.config(text=title)
            self.sub_label.config(text=subtitle)
            self.root.deiconify()
            self.root.lift()
        self.root.after(0, _update)

    def update_text(self, title, subtitle=None):
        """Cập nhật nội dung hiển thị trong lúc đang mở"""
        if not self.root:
            return
        def _update():
            self.title_label.config(text=title)
            if subtitle is not None:
                self.sub_label.config(text=subtitle)
        self.root.after(0, _update)

    def show_success(self, title, subtitle="", auto_hide_ms=2500):
        """Hiển thị kết quả thành công và tự động ẩn sau thời gian quy định"""
        if not self.root:
            return
        def _update():
            self.icon_label.config(text="✅")
            self.title_label.config(text=title)
            self.sub_label.config(text=subtitle)
            self.root.deiconify()
            self.root.lift()
            if self.hide_timer:
                self.root.after_cancel(self.hide_timer)
            self.hide_timer = self.root.after(auto_hide_ms, self._hide_now)
        self.root.after(0, _update)

    def show_error(self, title, subtitle="", auto_hide_ms=3000):
        """Hiển thị thông báo lỗi/chưa rõ và tự động ẩn"""
        if not self.root:
            return
        def _update():
            self.icon_label.config(text="❓")
            self.title_label.config(text=title)
            self.sub_label.config(text=subtitle)
            self.root.deiconify()
            self.root.lift()
            if self.hide_timer:
                self.root.after_cancel(self.hide_timer)
            self.hide_timer = self.root.after(auto_hide_ms, self._hide_now)
        self.root.after(0, _update)

    def _hide_now(self):
        if self.root:
            self.root.withdraw()
            self.hide_timer = None

    def hide(self):
        """Ẩn HUD ngay lập tức"""
        if self.root:
            self.root.after(0, self._hide_now)

if __name__ == "__main__":
    hud = AlexHUD()
    print("Testing HUD show...")
    hud.show("🎙️", "Alex đang nghe bạn nói...", "Mẹo: Nói 'OVER' để gửi nhanh")
    time.sleep(2)
    hud.update_text("Đang xử lý: 'Mở YouTube'...", "Vui lòng đợi trong giây lát")
    time.sleep(1.5)
    hud.show_success("Đã mở YouTube!", "Tác vụ hoàn thành trong 0.2s")
    time.sleep(3)
    print("Test finished.")
