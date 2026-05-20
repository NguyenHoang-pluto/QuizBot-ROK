import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from src.core.config import (
    THEME_MODE, PRIMARY_COLOR, SUCCESS_COLOR, BG_SIDEBAR, BG_IMAGE_PATH,
    OPT_Y_OFFSET_RATIO, OPT_X_OFFSET_RATIO, OPT_W_RATIO, OPT_H_RATIO, OPT_GAP_X_RATIO, OPT_GAP_Y_RATIO
)

ctk.set_appearance_mode(THEME_MODE)

class RegionSelector(tk.Toplevel):
    def __init__(self, callback, mode="question"):
        super().__init__()
        self.callback = callback
        self.mode = mode
        # Thiết lập độ trong suốt nhẹ 0.45 để nhìn rõ các đường kẻ căn chỉnh, vẫn giữ trọn màn hình game
        self.attributes("-alpha", 0.45, "-fullscreen", True, "-topmost", True)
        self.config(cursor="cross")
        self.canvas = tk.Canvas(self, cursor="cross", bg="grey")
        self.canvas.pack(fill="both", expand=True)
        self.start_x = self.start_y = self.rect = None
        
        # Kích thước màn hình
        self.screen_w = self.winfo_screenwidth()
        self.screen_h = self.winfo_screenheight()
        
        # Thiết lập màu sắc và tiêu đề theo chế độ quét
        if mode == "options":
            border_col = "#ffd700"
            text_str = "🎯 NHẤP GIỮ & KÉO CHUỘT ĐỂ KHOANH VÙNG ĐÁP ÁN TRÊN GAME (Nhấn ESC để hủy)"
            self.rect_color = "#ffd700"
        else:
            border_col = PRIMARY_COLOR
            text_str = "🎯 NHẤP GIỮ & KÉO CHUỘT ĐỂ KHOANH VÙNG CÂU HỎI TRÊN GAME (Nhấn ESC để hủy)"
            self.rect_color = "#ef4444"
            
        # Vẽ hộp hướng dẫn cực kỳ bắt mắt ở chính giữa đỉnh màn hình
        bar_w = 660
        bar_h = 42
        x1 = (self.screen_w - bar_w) // 2
        y1 = 25
        x2 = x1 + bar_w
        y2 = y1 + bar_h
        
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#121212", outline=border_col, width=2, tags="static_guide")
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, 
                                text=text_str, 
                                fill="#ffffff", font=("Arial", 11, "bold"), tags="static_guide")
        
        # Đăng ký các sự kiện di chuột, kéo chuột
        self.canvas.bind("<Motion>", self.draw_guides)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def draw_guides(self, event):
        x, y = event.x, event.y
        # Xóa tâm ngắm căn chỉnh cũ
        self.canvas.delete("crosshair")
        
        # Vẽ tâm ngắm màu vàng gold hoặc đỏ tùy chế độ chạy dọc và ngang màn hình giúp căn chỉnh vùng quét chuẩn xác từng pixel
        crosshair_color = "#ffd700" if self.mode == "options" else PRIMARY_COLOR
        self.canvas.create_line(0, y, self.screen_w, y, fill=crosshair_color, dash=(4, 4), tags="crosshair")
        self.canvas.create_line(x, 0, x, self.screen_h, fill=crosshair_color, dash=(4, 4), tags="crosshair")

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        # Tạo khung chữ nhật quét màu đỏ hoặc vàng tùy chế độ
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline=self.rect_color, width=4, tags="selection")

    def on_move_press(self, event):
        x, y = event.x, event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, x, y)
        
        # Vẽ lại tâm ngắm căn chỉnh khi đang kéo thả
        self.draw_guides(event)
        
        # Tính toán chiều rộng và chiều cao vùng quét thời gian thực
        w = abs(x - self.start_x)
        h = abs(y - self.start_y)
        
        # Xóa nhãn hiển thị kích thước cũ
        self.canvas.delete("dims")
        
        # Hiển thị nhãn thông số chạy theo trỏ chuột cực kỳ trực quan
        txt_x = x + 15
        txt_y = y + 20
        
        # Chống tràn nhãn kích thước ra ngoài mép màn hình phải hoặc dưới
        if txt_x + 160 > self.screen_w:
            txt_x = x - 165
        if txt_y + 30 > self.screen_h:
            txt_y = y - 32
            
        dim_str = f" Kích thước: {w} x {h} px "
        
        # Vẽ hộp nhãn thông số thời gian thực viền vàng/đỏ nền đen chuyên nghiệp
        border_col = "#ffd700" if self.mode == "options" else PRIMARY_COLOR
        text_id = self.canvas.create_text(txt_x, txt_y, text=dim_str, fill=SUCCESS_COLOR, font=("Arial", 10, "bold"), anchor="nw", tags="dims")
        bbox = self.canvas.bbox(text_id)
        if bbox:
            rect_id = self.canvas.create_rectangle(bbox[0]-4, bbox[1]-2, bbox[2]+4, bbox[3]+2, fill="#121212", outline=border_col, width=1, tags="dims")
            self.canvas.tag_lower(rect_id, text_id)

    def on_button_release(self, event):
        x, y = min(self.start_x, event.x), min(self.start_y, event.y)
        w, h = abs(self.start_x - event.x), abs(self.start_y - event.y)
        if w > 5 and h > 5: self.callback(x, y, w, h)
        self.destroy()

class OverlayQuestion(tk.Toplevel):
    def __init__(self, coord_callback=None, resize_callback=None):
        super().__init__()
        self.coord_callback = coord_callback
        self.resize_callback = resize_callback
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "white")
        
        self.drag_height = 18
        
        # Thanh kéo màu đỏ phía trên vùng khoanh
        self.drag_bar = tk.Frame(self, bg="#dc2626", height=self.drag_height)
        self.drag_bar.pack(fill="x", side="top")
        self.drag_bar.pack_propagate(False)
        
        self.drag_label = tk.Label(self.drag_bar, text="✥ VÙNG CÂU HỎI (Kéo để di chuyển)", fg="white", bg="#dc2626", font=("Arial", 8, "bold"))
        self.drag_label.pack(fill="both", expand=True)
        
        # Vùng trong suốt
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, side="bottom")
        
        self.rect = self.canvas.create_rectangle(0, 0, 0, 0, outline="#dc2626", width=2)
        
        # Grips
        self.grip_w = tk.Frame(self.canvas, bg="#dc2626", cursor="size_we", width=5, height=30)
        self.grip_h = tk.Frame(self.canvas, bg="#dc2626", cursor="size_ns", width=30, height=5)
        self.grip_corner = tk.Label(self.canvas, text="◢", fg="#dc2626", bg="white", cursor="size_nw_se", font=("Arial", 10, "bold"))
        
        self.withdraw()
        
        self.drag_bar.bind("<ButtonPress-1>", self.start_drag)
        self.drag_bar.bind("<B1-Motion>", self.on_drag)
        self.drag_label.bind("<ButtonPress-1>", self.start_drag)
        self.drag_label.bind("<B1-Motion>", self.on_drag)
        
        self.grip_w.bind("<ButtonPress-1>", self.start_resize_w)
        self.grip_w.bind("<B1-Motion>", self.on_resize_w)
        self.grip_h.bind("<ButtonPress-1>", self.start_resize_h)
        self.grip_h.bind("<B1-Motion>", self.on_resize_h)
        self.grip_corner.bind("<ButtonPress-1>", self.start_resize_corner)
        self.grip_corner.bind("<B1-Motion>", self.on_resize_corner)
        
        self._drag_data = {"x": 0, "y": 0}
        self._resize_start_size = {"w": 0, "h": 0}
        self.q_w = 0
        self.q_h = 0

    def show_region(self, x, y, w, h):
        self.q_w = w
        self.q_h = h
        self.geometry(f"{w}x{h + self.drag_height}+{x}+{y - self.drag_height}")
        self.canvas.config(width=w, height=h)
        self.canvas.coords(self.rect, 0, 0, w, h)
        
        self.grip_w.place(x=w, y=h // 2, anchor="e")
        self.grip_h.place(x=w // 2, y=h, anchor="s")
        self.grip_corner.place(x=w, y=h, anchor="se")
        self.deiconify()

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag(self, event):
        new_x = self.winfo_x() - self._drag_data["x"] + event.x
        new_y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{new_x}+{new_y}")
        if self.coord_callback:
            self.coord_callback(new_x, new_y + self.drag_height)

    def start_resize_w(self, event):
        self._drag_data["x"] = event.x_root
        self._resize_start_size["w"] = self.q_w

    def on_resize_w(self, event):
        delta_w = event.x_root - self._drag_data["x"]
        new_w = max(50, self._resize_start_size["w"] + delta_w)
        self.show_region(self.winfo_x(), self.winfo_y() + self.drag_height, new_w, self.q_h)
        if self.resize_callback:
            self.resize_callback(new_w, self.q_h)

    def start_resize_h(self, event):
        self._drag_data["y"] = event.y_root
        self._resize_start_size["h"] = self.q_h

    def on_resize_h(self, event):
        delta_h = event.y_root - self._drag_data["y"]
        new_h = max(30, self._resize_start_size["h"] + delta_h)
        self.show_region(self.winfo_x(), self.winfo_y() + self.drag_height, self.q_w, new_h)
        if self.resize_callback:
            self.resize_callback(self.q_w, new_h)

    def start_resize_corner(self, event):
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root
        self._resize_start_size["w"] = self.q_w
        self._resize_start_size["h"] = self.q_h

    def on_resize_corner(self, event):
        delta_w = event.x_root - self._drag_data["x"]
        delta_h = event.y_root - self._drag_data["y"]
        new_w = max(50, self._resize_start_size["w"] + delta_w)
        new_h = max(30, self._resize_start_size["h"] + delta_h)
        self.show_region(self.winfo_x(), self.winfo_y() + self.drag_height, new_w, new_h)
        if self.resize_callback:
            self.resize_callback(new_w, new_h)


class OverlayOptions(tk.Toplevel):
    def __init__(self, coord_callback=None, resize_callback=None):
        super().__init__()
        self.coord_callback = coord_callback
        self.resize_callback = resize_callback
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "white")
        
        self.drag_height = 18
        
        # Thanh kéo màu vàng/amber phía trên vùng khoanh
        self.drag_bar = tk.Frame(self, bg="#d97706", height=self.drag_height)
        self.drag_bar.pack(fill="x", side="top")
        self.drag_bar.pack_propagate(False)
        
        self.drag_label = tk.Label(self.drag_bar, text="✥ VÙNG ĐÁP ÁN (Kéo để di chuyển)", fg="white", bg="#d97706", font=("Arial", 8, "bold"))
        self.drag_label.pack(fill="both", expand=True)
        
        # Vùng trong suốt
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, side="bottom")
        
        self.rect = self.canvas.create_rectangle(0, 0, 0, 0, outline="#ffd700", width=2)
        
        # Các đường nét đứt phân chia 2x2
        self.grid_h_line = self.canvas.create_line(0, 0, 0, 0, fill="#ffd700", dash=(4, 4), width=1)
        self.grid_v_line = self.canvas.create_line(0, 0, 0, 0, fill="#ffd700", dash=(4, 4), width=1)
        
        # Các nhãn góc A, B, C, D
        self.lbl_a = self.canvas.create_text(0, 0, text="[A]", fill="#ffd700", font=("Arial", 10, "bold"), anchor="nw")
        self.lbl_b = self.canvas.create_text(0, 0, text="[B]", fill="#ffd700", font=("Arial", 10, "bold"), anchor="ne")
        self.lbl_c = self.canvas.create_text(0, 0, text="[C]", fill="#ffd700", font=("Arial", 10, "bold"), anchor="sw")
        self.lbl_d = self.canvas.create_text(0, 0, text="[D]", fill="#ffd700", font=("Arial", 10, "bold"), anchor="se")
        
        # Grips
        self.grip_w = tk.Frame(self.canvas, bg="#ffd700", cursor="size_we", width=5, height=30)
        self.grip_h = tk.Frame(self.canvas, bg="#ffd700", cursor="size_ns", width=30, height=5)
        self.grip_corner = tk.Label(self.canvas, text="◢", fg="#ffd700", bg="white", cursor="size_nw_se", font=("Arial", 10, "bold"))
        
        self.withdraw()
        
        self.drag_bar.bind("<ButtonPress-1>", self.start_drag)
        self.drag_bar.bind("<B1-Motion>", self.on_drag)
        self.drag_label.bind("<ButtonPress-1>", self.start_drag)
        self.drag_label.bind("<B1-Motion>", self.on_drag)
        
        self.grip_w.bind("<ButtonPress-1>", self.start_resize_w)
        self.grip_w.bind("<B1-Motion>", self.on_resize_w)
        self.grip_h.bind("<ButtonPress-1>", self.start_resize_h)
        self.grip_h.bind("<B1-Motion>", self.on_resize_h)
        self.grip_corner.bind("<ButtonPress-1>", self.start_resize_corner)
        self.grip_corner.bind("<B1-Motion>", self.on_resize_corner)
        
        self._drag_data = {"x": 0, "y": 0}
        self._resize_start_size = {"w": 0, "h": 0}
        self.opts_w = 0
        self.opts_h = 0

    def show_region(self, x, y, w, h):
        self.opts_w = w
        self.opts_h = h
        self.geometry(f"{w}x{h + self.drag_height}+{x}+{y - self.drag_height}")
        self.canvas.config(width=w, height=h)
        self.canvas.coords(self.rect, 0, 0, w, h)
        
        # Cập nhật đường phân chia 2x2
        mid_x = w // 2
        mid_y = h // 2
        self.canvas.coords(self.grid_h_line, 0, mid_y, w, mid_y)
        self.canvas.coords(self.grid_v_line, mid_x, 0, mid_x, h)
        
        # Cập nhật vị trí nhãn A, B, C, D
        self.canvas.coords(self.lbl_a, 5, 5)
        self.canvas.coords(self.lbl_b, w - 5, 5)
        self.canvas.coords(self.lbl_c, 5, h - 5)
        self.canvas.coords(self.lbl_d, w - 5, h - 5)
        
        self.grip_w.place(x=w, y=h // 2, anchor="e")
        self.grip_h.place(x=w // 2, y=h, anchor="s")
        self.grip_corner.place(x=w, y=h, anchor="se")
        self.deiconify()

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag(self, event):
        new_x = self.winfo_x() - self._drag_data["x"] + event.x
        new_y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{new_x}+{new_y}")
        if self.coord_callback:
            self.coord_callback(new_x, new_y + self.drag_height)

    def start_resize_w(self, event):
        self._drag_data["x"] = event.x_root
        self._resize_start_size["w"] = self.opts_w

    def on_resize_w(self, event):
        delta_w = event.x_root - self._drag_data["x"]
        new_w = max(50, self._resize_start_size["w"] + delta_w)
        self.show_region(self.winfo_x(), self.winfo_y() + self.drag_height, new_w, self.opts_h)
        if self.resize_callback:
            self.resize_callback(new_w, self.opts_h)

    def start_resize_h(self, event):
        self._drag_data["y"] = event.y_root
        self._resize_start_size["h"] = self.opts_h

    def on_resize_h(self, event):
        delta_h = event.y_root - self._drag_data["y"]
        new_h = max(30, self._resize_start_size["h"] + delta_h)
        self.show_region(self.winfo_x(), self.winfo_y() + self.drag_height, self.opts_w, new_h)
        if self.resize_callback:
            self.resize_callback(self.opts_w, new_h)

    def start_resize_corner(self, event):
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root
        self._resize_start_size["w"] = self.opts_w
        self._resize_start_size["h"] = self.opts_h

    def on_resize_corner(self, event):
        delta_w = event.x_root - self._drag_data["x"]
        delta_h = event.y_root - self._drag_data["y"]
        new_w = max(50, self._resize_start_size["w"] + delta_w)
        new_h = max(30, self._resize_start_size["h"] + delta_h)
        self.show_region(self.winfo_x(), self.winfo_y() + self.drag_height, new_w, new_h)
        if self.resize_callback:
            self.resize_callback(new_w, new_h)


class FloatingHUD(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.9)
        self.geometry("520x220+100+100")
        self.configure(bg="#121212")
        
        # Frame chính với viền vàng gold cực kỳ sang trọng
        self.frame = ctk.CTkFrame(self, fg_color="#121212", border_color=PRIMARY_COLOR, border_width=2, corner_radius=10)
        self.frame.pack(fill="both", expand=True)
        
        # Thanh tiêu đề phụ hỗ trợ kéo di chuyển
        self.title_label = ctk.CTkLabel(self.frame, text="⚡ ĐÁP ÁN HUD (Giữ chuột để kéo) ⚡", font=ctk.CTkFont(size=10, weight="bold"), text_color=PRIMARY_COLOR)
        self.title_label.pack(pady=(6, 2))
        
        # Nhãn câu hỏi nhận diện được (wraplength tăng lên 490 tương ứng rộng 520)
        self.lbl_question = ctk.CTkLabel(self.frame, text="Đang đợi câu hỏi...", font=ctk.CTkFont(size=11), text_color="#cccccc", wraplength=490, justify="center")
        self.lbl_question.pack(padx=10, pady=2, fill="x")
        
        # Nhãn gợi ý đáp án dạng Textbox cuộn mượt mà
        self.lbl_answer = ctk.CTkTextbox(self.frame, height=120, fg_color="transparent", text_color=SUCCESS_COLOR, font=ctk.CTkFont(size=13, weight="bold"), border_width=0, wrap="word")
        # Sử dụng khoảng đệm dưới 18px để lộ ra khoảng trống chứa nút grip ở góc dưới phải
        self.lbl_answer.pack(padx=10, pady=(2, 18), fill="both", expand=True)
        self.lbl_answer.insert("0.0", "CHƯA CÓ KẾT QUẢ")
        self.lbl_answer.configure(state="disabled")
        
        # Grip kéo góc dưới cùng bên phải để thay đổi kích thước HUD (màu vàng gold sang trọng)
        self.grip = tk.Label(self.frame, text="◢", fg=PRIMARY_COLOR, bg="#121212", cursor="size_nw_se", font=("Arial", 10, "bold"))
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.lift()
        
        self.withdraw()
        
        # Đăng ký kéo thả để di chuyển HUD
        for widget in [self, self.frame, self.title_label, self.lbl_question]:
            widget.bind("<ButtonPress-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.on_drag)
            
        # Đăng ký co giãn kích thước HUD
        self.grip.bind("<ButtonPress-1>", self.start_resize)
        self.grip.bind("<B1-Motion>", self.on_resize)
        
        self._drag_data = {"x": 0, "y": 0}
        self._resize_start_size = {"w": 0, "h": 0}

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag(self, event):
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root
        self._resize_start_size["w"] = self.winfo_width()
        self._resize_start_size["h"] = self.winfo_height()
        return "break"  # Ngăn sự kiện truyền lên widget cha (bubbling) gây di chuyển cửa sổ

    def on_resize(self, event):
        delta_w = event.x_root - self._drag_data["x"]
        delta_h = event.y_root - self._drag_data["y"]
        
        new_w = max(250, self._resize_start_size["w"] + delta_w)
        new_h = max(100, self._resize_start_size["h"] + delta_h)
        
        self.geometry(f"{new_w}x{new_h}")
        self.lbl_question.configure(wraplength=new_w - 30)
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.lift()
        return "break"  # Ngăn sự kiện truyền lên widget cha (bubbling) gây di chuyển cửa sổ

    def show_hud(self, x, y, w, h):
        """Hiển thị HUD gần vùng câu hỏi"""
        hud_x = x
        hud_y = y + h + 10
        self.geometry(f"+{hud_x}+{hud_y}")
        self.deiconify()

    def update_hud(self, q, a):
        self.lbl_question.configure(text=q)
        self.lbl_answer.configure(state="normal")
        self.lbl_answer.delete("0.0", "end")
        self.lbl_answer.insert("0.0", a)
        self.lbl_answer.configure(state="disabled")

class RoKQuizUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ULTIMATE QUIZ BOT: ROK & COD (PRO EDITION)")
        self.geometry("900x650")
        self.resizable(False, False)
        
        # 2 Khung đè Câu hỏi và Đáp án hoàn toàn độc lập
        self.overlay_q = OverlayQuestion(self.update_coords_q_from_drag, self.update_size_q_from_drag)
        self.overlay_opts = OverlayOptions(self.update_coords_opts_from_drag, self.update_size_opts_from_drag)
        self.hud = FloatingHUD()
        self.is_compact = False

        # Background
        if os.path.exists(BG_IMAGE_PATH):
            self.bg_image = ctk.CTkImage(Image.open(BG_IMAGE_PATH), size=(900, 650))
            self.bg_lbl = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)

        self.attributes("-topmost", True)
        
        # SIDEBAR PANEL
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=15, border_width=1, border_color=PRIMARY_COLOR, width=300, height=610)
        self.sidebar.place(x=20, y=20)
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="BẢNG ĐIỀU KHIỂN", font=ctk.CTkFont("Impact", 24), text_color=PRIMARY_COLOR).pack(pady=15)
        self.stats_label = ctk.CTkLabel(self.sidebar, text="Đang tải dữ liệu...", font=ctk.CTkFont(size=12))
        self.stats_label.pack(pady=5)
        
        ctk.CTkLabel(self.sidebar, text="CHỌN GAME:", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(10, 0))
        self.game_option = ctk.CTkOptionMenu(self.sidebar, values=["Rise of Kingdoms", "Call of Dragons"], fg_color="#374151", button_color=PRIMARY_COLOR)
        self.game_option.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(self.sidebar, text="DÁN LINK WEB CẦN CÀO:", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(10, 0))
        
        self.url_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.url_frame.pack(padx=20, pady=5, fill="x")
        
        self.entry_url = ctk.CTkEntry(self.url_frame, placeholder_text="https://...", height=32, fg_color="#0a0a0a")
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_clear_url = ctk.CTkButton(
            self.url_frame, 
            text="X", 
            width=32, 
            height=32, 
            fg_color="#dc2626", 
            hover_color="#b91c1c", 
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.clear_url_entry
        )
        self.btn_clear_url.pack(side="right")
        
        self.btn_crawl = ctk.CTkButton(self.sidebar, text="BẮT ĐẦU CÀO DỮ LIỆU", fg_color="#1e40af", height=32)
        self.btn_crawl.pack(pady=5, padx=20, fill="x")

        self.crawl_progress_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.crawl_progress_frame.pack(padx=20, pady=(2, 6), fill="x")
        
        self.lbl_crawl_progress = ctk.CTkLabel(self.crawl_progress_frame, text="Tiến độ cào: Sẵn sàng...", font=ctk.CTkFont(size=10, weight="bold"), text_color=PRIMARY_COLOR)
        self.lbl_crawl_progress.pack(anchor="w")
        
        self.crawl_progress = ctk.CTkProgressBar(self.crawl_progress_frame, height=8, progress_color=PRIMARY_COLOR, fg_color="#0a0a0a")
        self.crawl_progress.pack(fill="x", pady=(2, 0))
        self.crawl_progress.set(0)

        self.switch_sound = ctk.CTkSwitch(self.sidebar, text="ÂM BÁO KẾT QUẢ", font=ctk.CTkFont(size=11), progress_color=SUCCESS_COLOR)
        self.switch_sound.pack(pady=5, padx=20, anchor="w")
        self.switch_sound.select()

        self.switch_translate = ctk.CTkSwitch(self.sidebar, text="TỰ ĐỘNG DỊCH (EN->VI)", font=ctk.CTkFont(size=11), progress_color=SUCCESS_COLOR)
        self.switch_translate.pack(pady=5, padx=20, anchor="w")
        self.switch_translate.select()

        self.switch_hud = ctk.CTkSwitch(self.sidebar, text="HIỂN THỊ HUD ĐÁP ÁN", font=ctk.CTkFont(size=11), progress_color=SUCCESS_COLOR, command=self.toggle_hud_switch)
        self.switch_hud.pack(pady=5, padx=20, anchor="w")
        self.switch_hud.select()

        self.crawl_log = ctk.CTkTextbox(self.sidebar, height=120, font=ctk.CTkFont(size=10), fg_color="#0a0a0a", border_width=1)
        self.crawl_log.pack(padx=20, pady=5, fill="x")

        # MAIN PANEL AREA
        self.main_outer = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=15, border_width=2, border_color=PRIMARY_COLOR, width=540, height=610)
        self.main_outer.place(x=340, y=20)
        self.main_outer.pack_propagate(False)
        
        self.main_area = ctk.CTkScrollableFrame(self.main_outer, fg_color="transparent", corner_radius=15)
        self.main_area.pack(fill="both", expand=True, padx=2, pady=2)
        
        ctk.CTkLabel(self.main_area, text="NHẬN DIỆN CHIẾN TRƯỜNG", font=ctk.CTkFont("Impact", 28), text_color=PRIMARY_COLOR).pack(pady=15)

        # BẢNG THIẾT LẬP TỌA ĐỘ 2 KHU VỰC
        self.settings_frame = ctk.CTkFrame(self.main_area, fg_color="#2a2a2a", corner_radius=10)
        self.settings_frame.pack(padx=20, pady=5, fill="x")
        
        self.cols_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.cols_frame.pack(fill="x", padx=10, pady=5)
        
        # Cột trái: Vùng câu hỏi
        self.left_col = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.left_col.pack(side="left", expand=True, fill="both", padx=5)
        
        ctk.CTkLabel(self.left_col, text="VÙNG CÂU HỎI (ĐỎ)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#ef4444").pack(pady=(2, 5))
        
        self.coord_q_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        self.coord_q_frame.pack()
        
        self.entry_x_q = None
        self.entry_y_q = None
        self.entry_w_q = None
        self.entry_h_q = None
        
        for label, attr in [("X", "entry_x_q"), ("Y", "entry_y_q"), ("W", "entry_w_q"), ("H", "entry_h_q")]:
            f = ctk.CTkFrame(self.coord_q_frame, fg_color="transparent")
            f.pack(side="left", padx=2)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=9)).pack()
            e = ctk.CTkEntry(f, width=48, height=24, border_color="#ef4444", justify="center")
            e.pack()
            setattr(self, attr, e)
            
        self.btn_select_q = ctk.CTkButton(self.left_col, text="KHOANH CÂU HỎI", fg_color="#b91c1c", hover_color="#991b1b", height=28, font=ctk.CTkFont(size=11, weight="bold"))
        self.btn_select_q.pack(pady=8, fill="x")
        
        # Cột phải: Vùng đáp án
        self.right_col = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.right_col.pack(side="right", expand=True, fill="both", padx=5)
        
        ctk.CTkLabel(self.right_col, text="VÙNG ĐÁP ÁN (VÀNG)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#ffd700").pack(pady=(2, 5))
        
        self.coord_opts_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.coord_opts_frame.pack()
        
        self.entry_x_o = None
        self.entry_y_o = None
        self.entry_w_o = None
        self.entry_h_o = None
        
        for label, attr in [("X", "entry_x_o"), ("Y", "entry_y_o"), ("W", "entry_w_o"), ("H", "entry_h_o")]:
            f = ctk.CTkFrame(self.coord_opts_frame, fg_color="transparent")
            f.pack(side="left", padx=2)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=9)).pack()
            e = ctk.CTkEntry(f, width=48, height=24, border_color="#ffd700", justify="center")
            e.pack()
            setattr(self, attr, e)
            
        self.btn_select_opts = ctk.CTkButton(self.right_col, text="KHOANH ĐÁP ÁN", fg_color="#d97706", hover_color="#b45309", height=28, font=ctk.CTkFont(size=11, weight="bold"))
        self.btn_select_opts.pack(pady=8, fill="x")

        # Đăng ký đồng bộ ngược khi gõ phím trực tiếp
        for entry in [self.entry_x_q, self.entry_y_q, self.entry_w_q, self.entry_h_q]:
            entry.bind("<KeyRelease>", self.update_q_overlay_from_entry)
            
        for entry in [self.entry_x_o, self.entry_y_o, self.entry_w_o, self.entry_h_o]:
            entry.bind("<KeyRelease>", self.update_opts_overlay_from_entry)

        # Thanh trượt chỉnh độ mờ
        self.opacity_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.opacity_frame.pack(padx=20, pady=(2, 8), fill="x")
        ctk.CTkLabel(self.opacity_frame, text="ĐỘ MỜ GIAO DIỆN:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 10))
        self.opacity_slider = ctk.CTkSlider(self.opacity_frame, from_=0.2, to=1.0, number_of_steps=80, button_color=PRIMARY_COLOR, progress_color=PRIMARY_COLOR, command=self.change_opacity)
        self.opacity_slider.pack(side="right", fill="x", expand=True)
        self.opacity_slider.set(1.0)

        # Kết quả nhận diện
        self.res_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.res_frame.pack(padx=20, pady=5, fill="both", expand=True)
        ctk.CTkLabel(self.res_frame, text="CÂU HỎI NHẬN DIỆN ĐƯỢC:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaaaaa").pack(anchor="w")
        self.txt_question = ctk.CTkTextbox(self.res_frame, height=65, fg_color="#0f0f0f", border_width=1)
        self.txt_question.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(self.res_frame, text="ĐÁP ÁN GỢI Ý:", font=ctk.CTkFont(size=12, weight="bold"), text_color=SUCCESS_COLOR).pack(anchor="w")
        self.txt_answer = ctk.CTkTextbox(self.res_frame, height=110, fg_color="#0f0f0f", border_color=SUCCESS_COLOR, text_color=SUCCESS_COLOR, font=ctk.CTkFont(size=13, weight="bold"))
        self.txt_answer.pack(fill="x")

        self.btn_save_db = ctk.CTkButton(self.res_frame, text="💾 LƯU / CẬP NHẬT ĐÁP ÁN VÀO DATABASE", fg_color=SUCCESS_COLOR, hover_color="#059669", height=38, font=ctk.CTkFont(size=13, weight="bold"))
        self.btn_save_db.pack(fill="x", pady=(8, 0))

        self.status_text = ctk.CTkLabel(self.main_area, text="TRẠNG THÁI: CHỜ LỆNH", text_color="#ef4444", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_text.pack(pady=5)
        
        # Khung nút điều khiển chính
        self.control_btn_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.control_btn_frame.pack(padx=20, pady=(0, 15), fill="x")
        
        self.btn_compact = ctk.CTkButton(self.control_btn_frame, text="THU NHỎ 🗕", fg_color="#374151", hover_color="#4b5563", height=50, width=120, font=ctk.CTkFont(size=14, weight="bold"), command=self.toggle_compact_mode)
        self.btn_compact.pack(side="left", padx=(0, 10))

        self.btn_start = ctk.CTkButton(self.control_btn_frame, text="BẬT BOT TỰ ĐỘNG (F4)", fg_color="#b45309", hover_color="#92400e", height=50, corner_radius=10, font=ctk.CTkFont(size=18, weight="bold"))
        self.btn_start.pack(side="right", fill="x", expand=True)

        # COMPACT MODE PANEL
        self.compact_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=15, border_width=2, border_color=PRIMARY_COLOR, width=380, height=425)
        self.compact_frame.pack_propagate(False)
        
        ctk.CTkLabel(self.compact_frame, text="⚡ BẢNG THU NHỎ (F4) ⚡", font=ctk.CTkFont("Impact", 18), text_color=PRIMARY_COLOR).pack(pady=(10, 5))
        
        ctk.CTkLabel(self.compact_frame, text="CÂU HỎI:", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaaaaa").pack(anchor="w", padx=15)
        self.txt_question_compact = ctk.CTkTextbox(self.compact_frame, height=65, fg_color="#0f0f0f", border_width=1, font=ctk.CTkFont(size=11), wrap="word")
        self.txt_question_compact.pack(fill="x", padx=15, pady=(0, 5))
        
        ctk.CTkLabel(self.compact_frame, text="ĐÁP ÁN GỢI Ý:", font=ctk.CTkFont(size=10, weight="bold"), text_color=SUCCESS_COLOR).pack(anchor="w", padx=15)
        self.txt_answer_compact = ctk.CTkTextbox(self.compact_frame, height=100, fg_color="#0f0f0f", border_color=SUCCESS_COLOR, text_color=SUCCESS_COLOR, font=ctk.CTkFont(size=13, weight="bold"), wrap="word")
        self.txt_answer_compact.pack(fill="x", padx=15, pady=(0, 10))
        
        self.btn_save_db_compact = ctk.CTkButton(self.compact_frame, text="💾 LƯU / CẬP NHẬT ĐÁP ÁN VÀO DB", fg_color=SUCCESS_COLOR, hover_color="#059669", height=38, font=ctk.CTkFont(size=12, weight="bold"))
        self.btn_save_db_compact.pack(fill="x", padx=15, pady=(0, 8))
        
        self.compact_btn_frame = ctk.CTkFrame(self.compact_frame, fg_color="transparent")
        self.compact_btn_frame.pack(fill="x", padx=15, pady=5)
        
        self.btn_start_compact = ctk.CTkButton(self.compact_btn_frame, text="BẬT BOT", fg_color="#b45309", hover_color="#92400e", height=40, font=ctk.CTkFont(size=13, weight="bold"))
        self.btn_start_compact.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_full_mode = ctk.CTkButton(self.compact_btn_frame, text="ĐẦY ĐỦ 🗖", fg_color="#374151", hover_color="#4b5563", height=40, width=90, font=ctk.CTkFont(size=13, weight="bold"), command=self.toggle_compact_mode)
        self.btn_full_mode.pack(side="right")

    def get_coords_q(self):
        try: return (int(self.entry_x_q.get()), int(self.entry_y_q.get()), int(self.entry_w_q.get()), int(self.entry_h_q.get()))
        except: return (0, 0, 0, 0)

    def get_coords_opts(self):
        try: return (int(self.entry_x_o.get()), int(self.entry_y_o.get()), int(self.entry_w_o.get()), int(self.entry_h_o.get()))
        except: return (0, 0, 0, 0)

    def update_coords_q(self, x, y, w, h):
        for e, v in zip([self.entry_x_q, self.entry_y_q, self.entry_w_q, self.entry_h_q], [x, y, w, h]):
            e.delete(0, "end")
            e.insert(0, str(v))
        self.overlay_q.show_region(x, y, w, h)
        if self.switch_hud.get() and "TẮT" in self.btn_start.cget("text"):
            self.hud.show_hud(x, y, w, h)

    def update_coords_opts(self, x, y, w, h):
        for e, v in zip([self.entry_x_o, self.entry_y_o, self.entry_w_o, self.entry_h_o], [x, y, w, h]):
            e.delete(0, "end")
            e.insert(0, str(v))
        self.overlay_opts.show_region(x, y, w, h)

    def update_q_overlay_from_entry(self, event=None):
        coords = self.get_coords_q()
        if coords != (0, 0, 0, 0):
            self.overlay_q.show_region(*coords)
            if self.switch_hud.get() and "TẮT" in self.btn_start.cget("text"):
                self.hud.show_hud(*coords)

    def update_opts_overlay_from_entry(self, event=None):
        coords = self.get_coords_opts()
        if coords != (0, 0, 0, 0):
            self.overlay_opts.show_region(*coords)

    def update_qa(self, q, a):
        self.txt_question.delete("0.0", "end")
        self.txt_answer.delete("0.0", "end")
        self.txt_question.insert("0.0", q)
        self.txt_answer.insert("0.0", a)
            
        self.txt_question_compact.delete("0.0", "end")
        self.txt_answer_compact.delete("0.0", "end")
        self.txt_question_compact.insert("0.0", q)
        self.txt_answer_compact.insert("0.0", a)
            
        self.hud.update_hud(q, a)

    def update_stats(self, text): 
        self.stats_label.configure(text=text)
        
    def start_selection(self, callback, mode="question"): 
        RegionSelector(callback, mode=mode)

    def clear_url_entry(self):
        self.entry_url.delete(0, "end")

    def change_opacity(self, val):
        self.attributes("-alpha", float(val))

    def toggle_hud_switch(self):
        if not self.switch_hud.get():
            self.hud.withdraw()
        else:
            if "TẮT" in self.btn_start.cget("text"):
                lx, ly, lw, lh = self.get_coords_q()
                self.hud.show_hud(lx, ly, lw, lh)

    def toggle_compact_mode(self):
        self.is_compact = not self.is_compact
        if self.is_compact:
            if hasattr(self, "bg_lbl"):
                self.bg_lbl.place_forget()
            self.sidebar.place_forget()
            self.main_outer.place_forget()
            
            self.geometry("400x380")
            self.compact_frame.place(x=10, y=10)
        else:
            self.compact_frame.place_forget()
            self.geometry("900x650")
            
            if hasattr(self, "bg_lbl"):
                self.bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)
            self.sidebar.place(x=20, y=20)
            self.main_outer.place(x=340, y=20)

    def update_coords_q_from_drag(self, x, y):
        self.entry_x_q.delete(0, "end")
        self.entry_x_q.insert(0, str(int(x)))
        self.entry_y_q.delete(0, "end")
        self.entry_y_q.insert(0, str(int(y)))
        if self.switch_hud.get() and "TẮT" in self.btn_start.cget("text"):
            try:
                w = int(self.entry_w_q.get())
                h = int(self.entry_h_q.get())
                self.hud.show_hud(x, y, w, h)
            except Exception as e:
                print(f"[HUD DRAG UPDATE ERROR]: {e}")

    def update_size_q_from_drag(self, w, h):
        self.entry_w_q.delete(0, "end")
        self.entry_w_q.insert(0, str(int(w)))
        self.entry_h_q.delete(0, "end")
        self.entry_h_q.insert(0, str(int(h)))
        if self.switch_hud.get() and "TẮT" in self.btn_start.cget("text"):
            try:
                x = int(self.entry_x_q.get())
                y = int(self.entry_y_q.get())
                self.hud.show_hud(x, y, w, h)
            except Exception as e:
                print(f"[HUD DRAG UPDATE ERROR]: {e}")

    def update_coords_opts_from_drag(self, x, y):
        self.entry_x_o.delete(0, "end")
        self.entry_x_o.insert(0, str(int(x)))
        self.entry_y_o.delete(0, "end")
        self.entry_y_o.insert(0, str(int(y)))

    def update_size_opts_from_drag(self, w, h):
        self.entry_w_o.delete(0, "end")
        self.entry_w_o.insert(0, str(int(w)))
        self.entry_h_o.delete(0, "end")
        self.entry_h_o.insert(0, str(int(h)))
