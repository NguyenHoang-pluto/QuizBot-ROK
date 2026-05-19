import customtkinter as ctk
from PIL import Image
import os
import tkinter as tk
from src.core.config import THEME_MODE, PRIMARY_COLOR, SUCCESS_COLOR, BG_SIDEBAR, BG_IMAGE_PATH

ctk.set_appearance_mode(THEME_MODE)

class RegionSelector(tk.Toplevel):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.attributes("-alpha", 0.3, "-fullscreen", True, "-topmost", True)
        self.config(cursor="cross")
        self.canvas = tk.Canvas(self, cursor="cross", bg="grey")
        self.canvas.pack(fill="both", expand=True)
        self.start_x = self.start_y = self.rect = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline="red", width=3)

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        x, y = min(self.start_x, event.x), min(self.start_y, event.y)
        w, h = abs(self.start_x - event.x), abs(self.start_y - event.y)
        if w > 5 and h > 5: self.callback(x, y, w, h)
        self.destroy()

class OverlayBorder(tk.Toplevel):
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
        
        self.drag_label = tk.Label(self.drag_bar, text="✥ VÙNG QUÉT (Nhấp giữ để kéo)", fg="white", bg="#dc2626", font=("Arial", 8, "bold"))
        self.drag_label.pack(fill="both", expand=True)
        
        # Vùng trong suốt có viền đỏ
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, side="bottom")
        self.rect = self.canvas.create_rectangle(0, 0, 0, 0, outline="#dc2626", width=2)
        
        # 1. Grip kéo cạnh phải để thay đổi CHIỀU RỘNG (W)
        self.grip_w = tk.Frame(self.canvas, bg="#dc2626", cursor="size_we", width=5, height=30)
        self.grip_w.place(relx=1.0, rely=0.5, anchor="e")
        
        # 2. Grip kéo cạnh dưới để thay đổi CHIỀU CAO (H)
        self.grip_h = tk.Frame(self.canvas, bg="#dc2626", cursor="size_ns", width=30, height=5)
        self.grip_h.place(relx=0.5, rely=1.0, anchor="s")
        
        # 3. Grip góc dưới cùng bên phải để thay đổi CẢ HAI cùng lúc
        self.grip_corner = tk.Label(self.canvas, text="◢", fg="#dc2626", bg="white", cursor="size_nw_se", font=("Arial", 10, "bold"))
        self.grip_corner.place(relx=1.0, rely=1.0, anchor="se")
        
        self.withdraw()
        
        # Bắt sự kiện kéo di chuyển
        self.drag_bar.bind("<ButtonPress-1>", self.start_drag)
        self.drag_bar.bind("<B1-Motion>", self.on_drag)
        self.drag_label.bind("<ButtonPress-1>", self.start_drag)
        self.drag_label.bind("<B1-Motion>", self.on_drag)
        
        # Bắt sự kiện co giãn
        self.grip_w.bind("<ButtonPress-1>", self.start_resize_w)
        self.grip_w.bind("<B1-Motion>", self.on_resize_w)
        
        self.grip_h.bind("<ButtonPress-1>", self.start_resize_h)
        self.grip_h.bind("<B1-Motion>", self.on_resize_h)
        
        self.grip_corner.bind("<ButtonPress-1>", self.start_resize_corner)
        self.grip_corner.bind("<B1-Motion>", self.on_resize_corner)
        
        self._drag_data = {"x": 0, "y": 0}
        self._resize_start_size = {"w": 0, "h": 0}

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag(self, event):
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{x}+{y}")
        if self.coord_callback:
            self.coord_callback(x, y + self.drag_height)

    # --- KÉO CHIỀU RỘNG (W) ---
    def start_resize_w(self, event):
        self._drag_data["x"] = event.x_root
        self._resize_start_size["w"] = self.winfo_width()

    def on_resize_w(self, event):
        delta_w = event.x_root - self._drag_data["x"]
        new_w = max(50, self._resize_start_size["w"] + delta_w)
        new_h = self.winfo_height() - self.drag_height
        
        self.geometry(f"{new_w}x{new_h + self.drag_height}")
        self.canvas.config(width=new_w, height=new_h)
        self.canvas.coords(self.rect, 1, 1, new_w-1, new_h-1)
        
        # Đồng bộ vị trí các grip
        self.grip_w.place(relx=1.0, rely=0.5, anchor="e")
        self.grip_h.place(relx=0.5, rely=1.0, anchor="s")
        self.grip_corner.place(relx=1.0, rely=1.0, anchor="se")
        
        if self.resize_callback:
            self.resize_callback(new_w, new_h)

    # --- KÉO CHIỀU CAO (H) ---
    def start_resize_h(self, event):
        self._drag_data["y"] = event.y_root
        self._resize_start_size["h"] = self.winfo_height() - self.drag_height

    def on_resize_h(self, event):
        delta_h = event.y_root - self._drag_data["y"]
        new_w = self.winfo_width()
        new_h = max(30, self._resize_start_size["h"] + delta_h)
        
        self.geometry(f"{new_w}x{new_h + self.drag_height}")
        self.canvas.config(width=new_w, height=new_h)
        self.canvas.coords(self.rect, 1, 1, new_w-1, new_h-1)
        
        # Đồng bộ vị trí các grip
        self.grip_w.place(relx=1.0, rely=0.5, anchor="e")
        self.grip_h.place(relx=0.5, rely=1.0, anchor="s")
        self.grip_corner.place(relx=1.0, rely=1.0, anchor="se")
        
        if self.resize_callback:
            self.resize_callback(new_w, new_h)

    # --- KÉO GÓC ĐỒNG THỜI (W & H) ---
    def start_resize_corner(self, event):
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root
        self._resize_start_size["w"] = self.winfo_width()
        self._resize_start_size["h"] = self.winfo_height() - self.drag_height

    def on_resize_corner(self, event):
        delta_w = event.x_root - self._drag_data["x"]
        delta_h = event.y_root - self._drag_data["y"]
        
        new_w = max(50, self._resize_start_size["w"] + delta_w)
        new_h = max(30, self._resize_start_size["h"] + delta_h)
        
        self.geometry(f"{new_w}x{new_h + self.drag_height}")
        self.canvas.config(width=new_w, height=new_h)
        self.canvas.coords(self.rect, 1, 1, new_w-1, new_h-1)
        
        # Đồng bộ vị trí các grip
        self.grip_w.place(relx=1.0, rely=0.5, anchor="e")
        self.grip_h.place(relx=0.5, rely=1.0, anchor="s")
        self.grip_corner.place(relx=1.0, rely=1.0, anchor="se")
        
        if self.resize_callback:
            self.resize_callback(new_w, new_h)

    def show_region(self, x, y, w, h):
        self.geometry(f"{w}x{h + self.drag_height}+{x}+{y - self.drag_height}")
        self.canvas.config(width=w, height=h)
        self.canvas.coords(self.rect, 1, 1, w-1, h-1)
        self.grip_w.place(relx=1.0, rely=0.5, anchor="e")
        self.grip_h.place(relx=0.5, rely=1.0, anchor="s")
        self.grip_corner.place(relx=1.0, rely=1.0, anchor="se")
        self.deiconify()

class FloatingHUD(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.9)
        self.geometry("450x180+100+100")
        self.configure(bg="#121212")
        
        # Frame chính với viền vàng gold cực kỳ sang trọng
        self.frame = ctk.CTkFrame(self, fg_color="#121212", border_color=PRIMARY_COLOR, border_width=2, corner_radius=10)
        self.frame.pack(fill="both", expand=True)
        
        # Thanh tiêu đề phụ hỗ trợ kéo di chuyển
        self.title_label = ctk.CTkLabel(self.frame, text="⚡ ĐÁP ÁN HUD (Giữ chuột để kéo) ⚡", font=ctk.CTkFont(size=10, weight="bold"), text_color=PRIMARY_COLOR)
        self.title_label.pack(pady=(6, 2))
        
        # Nhãn câu hỏi nhận diện được
        self.lbl_question = ctk.CTkLabel(self.frame, text="Đang đợi câu hỏi...", font=ctk.CTkFont(size=11), text_color="#cccccc", wraplength=420, justify="center")
        self.lbl_question.pack(padx=10, pady=2, fill="x")
        
        # Nhãn gợi ý đáp án dạng Textbox cuộn mượt mà
        self.lbl_answer = ctk.CTkTextbox(self.frame, height=90, fg_color="transparent", text_color=SUCCESS_COLOR, font=ctk.CTkFont(size=13, weight="bold"), border_width=0, wrap="word")
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

    def update_hud(self, q, a):
        self.lbl_question.configure(text=q)
        self.lbl_answer.configure(state="normal")
        self.lbl_answer.delete("0.0", "end")
        self.lbl_answer.insert("0.0", a)
        self.lbl_answer.configure(state="disabled")

    def show_hud(self, x, y, w, h):
        # Lấy kích thước hiện tại của HUD để giữ nguyên khi mở lại
        hud_w = self.winfo_width()
        hud_h = self.winfo_height()
        if hud_w < 100 or hud_h < 50:
            hud_w = 450
            hud_h = 180
            
        # Tự động hiển thị phía dưới vùng quét 10 pixel
        hud_x = x
        hud_y = y + h + 10
        
        # Nếu vượt quá mép dưới màn hình thì đẩy lên trên vùng quét
        screen_height = self.winfo_screenheight()
        if hud_y + hud_h > screen_height:
            hud_y = max(0, y - hud_h - 10)
            
        self.geometry(f"{hud_w}x{hud_h}+{hud_x}+{hud_y}")
        self.lbl_question.configure(wraplength=hud_w - 30)
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.lift()
        self.deiconify()

class RoKQuizUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ULTIMATE QUIZ BOT: ROK & COD (PRO EDITION)")
        self.geometry("900x650")
        self.resizable(False, False)
        self.overlay = OverlayBorder(self.update_coords_from_drag, self.update_size_from_drag)
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
        self.sidebar.place(x=20, y=20); self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="BẢNG ĐIỀU KHIỂN", font=ctk.CTkFont("Impact", 24), text_color=PRIMARY_COLOR).pack(pady=15)
        self.stats_label = ctk.CTkLabel(self.sidebar, text="Đang tải dữ liệu...", font=ctk.CTkFont(size=12)); self.stats_label.pack(pady=5)
        
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

        # Khung hiển thị tiến độ cào mượt mà với phần trăm và số lượng cụ thể
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

        # Switch hiển thị HUD đáp án cực kỳ tiện lợi
        self.switch_hud = ctk.CTkSwitch(self.sidebar, text="HIỂN THỊ HUD ĐÁP ÁN", font=ctk.CTkFont(size=11), progress_color=SUCCESS_COLOR, command=self.toggle_hud_switch)
        self.switch_hud.pack(pady=5, padx=20, anchor="w")
        self.switch_hud.select()

        self.crawl_log = ctk.CTkTextbox(self.sidebar, height=120, font=ctk.CTkFont(size=10), fg_color="#0a0a0a", border_width=1)
        self.crawl_log.pack(padx=20, pady=5, fill="x")

        # MAIN PANEL AREA
        self.main_area = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=15, border_width=2, border_color=PRIMARY_COLOR, width=540, height=610)
        self.main_area.place(x=340, y=20); self.main_area.pack_propagate(False)
        ctk.CTkLabel(self.main_area, text="NHẬN DIỆN CHIẾN TRƯỜNG", font=ctk.CTkFont("Impact", 28), text_color=PRIMARY_COLOR).pack(pady=15)

        self.settings_frame = ctk.CTkFrame(self.main_area, fg_color="#2a2a2a", corner_radius=10); self.settings_frame.pack(padx=20, pady=5, fill="x")
        self.coord_container = ctk.CTkFrame(self.settings_frame, fg_color="transparent"); self.coord_container.pack(pady=5)
        for label, attr in [("X", "entry_x"), ("Y", "entry_y"), ("W", "entry_w"), ("H", "entry_h")]:
            f = ctk.CTkFrame(self.coord_container, fg_color="transparent"); f.pack(side="left", padx=5)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=10)).pack()
            e = ctk.CTkEntry(f, width=55, height=28, border_color=PRIMARY_COLOR, justify="center"); e.pack(); setattr(self, attr, e)
        
        self.btn_select_region = ctk.CTkButton(self.settings_frame, text="CHỌN VÙNG TRÊN MÀN HÌNH", fg_color="#374151", height=35); self.btn_select_region.pack(padx=20, pady=5, fill="x")

        # Thanh trượt chỉnh độ mờ (transparency) cực kỳ xịn sò
        self.opacity_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.opacity_frame.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(self.opacity_frame, text="ĐỘ MỜ GIAO DIỆN:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 10))
        self.opacity_slider = ctk.CTkSlider(self.opacity_frame, from_=0.2, to=1.0, number_of_steps=80, button_color=PRIMARY_COLOR, progress_color=PRIMARY_COLOR, command=self.change_opacity)
        self.opacity_slider.pack(side="right", fill="x", expand=True)
        self.opacity_slider.set(1.0)

        self.res_frame = ctk.CTkFrame(self.main_area, fg_color="transparent"); self.res_frame.pack(padx=20, pady=5, fill="both", expand=True)
        ctk.CTkLabel(self.res_frame, text="CÂU HỎI NHẬN DIỆN ĐƯỢC:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaaaaa").pack(anchor="w")
        self.txt_question = ctk.CTkTextbox(self.res_frame, height=65, fg_color="#0f0f0f", border_width=1); self.txt_question.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(self.res_frame, text="ĐÁP ÁN GỢI Ý:", font=ctk.CTkFont(size=12, weight="bold"), text_color=SUCCESS_COLOR).pack(anchor="w")
        self.txt_answer = ctk.CTkTextbox(self.res_frame, height=65, fg_color="#0f0f0f", border_color=SUCCESS_COLOR, text_color=SUCCESS_COLOR, font=ctk.CTkFont(size=20, weight="bold")); self.txt_answer.pack(fill="x")
        
        self.btn_save_db = ctk.CTkButton(self.res_frame, text="💾 LƯU / CẬP NHẬT ĐÁP ÁN VÀO DATABASE", fg_color=SUCCESS_COLOR, hover_color="#059669", height=38, font=ctk.CTkFont(size=13, weight="bold"))
        self.btn_save_db.pack(fill="x", pady=(8, 0))

        self.status_text = ctk.CTkLabel(self.main_area, text="TRẠNG THÁI: CHỜ LỆNH", text_color="#ef4444", font=ctk.CTkFont(size=16, weight="bold")); self.status_text.pack(pady=5)
        
        # Khung chứa các nút điều khiển chính
        self.control_btn_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.control_btn_frame.pack(padx=20, pady=(0, 15), fill="x")
        
        self.btn_compact = ctk.CTkButton(self.control_btn_frame, text="THU NHỎ 🗕", fg_color="#374151", hover_color="#4b5563", height=50, width=120, font=ctk.CTkFont(size=14, weight="bold"), command=self.toggle_compact_mode)
        self.btn_compact.pack(side="left", padx=(0, 10))

        self.btn_start = ctk.CTkButton(self.control_btn_frame, text="BẬT BOT TỰ ĐỘNG (F4)", fg_color="#b45309", hover_color="#92400e", height=50, corner_radius=10, font=ctk.CTkFont(size=18, weight="bold"))
        self.btn_start.pack(side="right", fill="x", expand=True)

        # COMPACT MODE PANEL (Ẩn ban đầu, tăng chiều cao lên 425 để chứa nút lưu)
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

    def get_coords(self):
        try: return (int(self.entry_x.get()), int(self.entry_y.get()), int(self.entry_w.get()), int(self.entry_h.get()))
        except: return (0,0,0,0)

    def update_coords(self, x,y,w,h):
        for e, v in zip([self.entry_x, self.entry_y, self.entry_w, self.entry_h], [x,y,w,h]):
            e.delete(0, "end"); e.insert(0, str(v))
        self.overlay.show_region(x, y, w, h)
        if self.switch_hud.get() and "TẮT" in self.btn_start.cget("text"):
            self.hud.show_hud(x, y, w, h)

    def update_qa(self, q, a):
        # Update chính
        self.txt_question.delete("0.0", "end")
        self.txt_answer.delete("0.0", "end")
        self.txt_question.insert("0.0", q)
        self.txt_answer.insert("0.0", a)
            
        # Update compact panel
        self.txt_question_compact.delete("0.0", "end")
        self.txt_answer_compact.delete("0.0", "end")
        self.txt_question_compact.insert("0.0", q)
        self.txt_answer_compact.insert("0.0", a)
            
        # Update HUD
        self.hud.update_hud(q, a)

    def update_stats(self, text): self.stats_label.configure(text=text)
    def start_selection(self, callback): RegionSelector(callback)

    def clear_url_entry(self):
        self.entry_url.delete(0, "end")

    def change_opacity(self, val):
        self.attributes("-alpha", float(val))

    def toggle_hud_switch(self):
        if not self.switch_hud.get():
            self.hud.withdraw()
        else:
            if "TẮT" in self.btn_start.cget("text"):
                lx, ly, lw, lh = self.get_coords()
                self.hud.show_hud(lx, ly, lw, lh)

    def toggle_compact_mode(self):
        self.is_compact = not self.is_compact
        if self.is_compact:
            if hasattr(self, "bg_lbl"):
                self.bg_lbl.place_forget()
            self.sidebar.place_forget()
            self.main_area.place_forget()
            
            self.geometry("400x380")
            self.compact_frame.place(x=10, y=10)
        else:
            self.compact_frame.place_forget()
            self.geometry("900x650")
            
            if hasattr(self, "bg_lbl"):
                self.bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)
            self.sidebar.place(x=20, y=20)
            self.main_area.place(x=340, y=20)

    def update_coords_from_drag(self, x, y):
        # Cập nhật tọa độ vào ô nhập liệu X và Y trên giao diện
        self.entry_x.delete(0, "end")
        self.entry_x.insert(0, str(x))
        self.entry_y.delete(0, "end")
        self.entry_y.insert(0, str(y))
        
        # Đồng bộ hóa vị trí HUD nếu đang bật
        if self.switch_hud.get() and "TẮT" in self.btn_start.cget("text"):
            try:
                w = int(self.entry_w.get())
                h = int(self.entry_h.get())
                self.hud.show_hud(x, y, w, h)
            except Exception as e:
                print(f"[HUD DRAG UPDATE ERROR]: {e}")

    def update_size_from_drag(self, w, h):
        # Cập nhật kích thước vào ô nhập liệu W và H trên giao diện
        self.entry_w.delete(0, "end")
        self.entry_w.insert(0, str(w))
        self.entry_h.delete(0, "end")
        self.entry_h.insert(0, str(h))
        
        # Đồng bộ hóa lại HUD nếu đang hoạt động
        if self.switch_hud.get() and "TẮT" in self.btn_start.cget("text"):
            try:
                x = int(self.entry_x.get())
                y = int(self.entry_y.get())
                self.hud.show_hud(x, y, w, h)
            except Exception as e:
                pass
