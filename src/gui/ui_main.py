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
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "white")
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.rect = self.canvas.create_rectangle(0, 0, 0, 0, outline="red", width=2)
        self.withdraw()

    def show_region(self, x, y, w, h):
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.canvas.config(width=w, height=h)
        self.canvas.coords(self.rect, 1, 1, w-1, h-1)
        self.deiconify()

class RoKQuizUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ULTIMATE QUIZ BOT: ROK & COD (PRO EDITION)")
        self.geometry("900x650")
        self.resizable(False, False)
        self.overlay = OverlayBorder()

        # Background
        if os.path.exists(BG_IMAGE_PATH):
            self.bg_image = ctk.CTkImage(Image.open(BG_IMAGE_PATH), size=(900, 650))
            ctk.CTkLabel(self, image=self.bg_image, text="").place(x=0, y=0, relwidth=1, relheight=1)

        self.attributes("-topmost", True)
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=15, border_width=1, border_color=PRIMARY_COLOR, width=300, height=610)
        self.sidebar.place(x=20, y=20); self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="BẢNG ĐIỀU KHIỂN", font=ctk.CTkFont("Impact", 24), text_color=PRIMARY_COLOR).pack(pady=15)
        self.stats_label = ctk.CTkLabel(self.sidebar, text="Đang tải dữ liệu...", font=ctk.CTkFont(size=12)); self.stats_label.pack(pady=5)
        
        ctk.CTkLabel(self.sidebar, text="CHỌN GAME:", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(10, 0))
        self.game_option = ctk.CTkOptionMenu(self.sidebar, values=["Rise of Kingdoms", "Call of Dragons"], fg_color="#374151", button_color=PRIMARY_COLOR)
        self.game_option.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(self.sidebar, text="DÁN LINK WEB CẦN CÀO:", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(10, 0))
        self.entry_url = ctk.CTkEntry(self.sidebar, placeholder_text="https://...", height=32, fg_color="#0a0a0a")
        self.entry_url.pack(padx=20, pady=5, fill="x")
        self.btn_crawl = ctk.CTkButton(self.sidebar, text="BẮT ĐẦU CÀO DỮ LIỆU", fg_color="#1e40af", height=32)
        self.btn_crawl.pack(pady=5, padx=20, fill="x")

        self.switch_sound = ctk.CTkSwitch(self.sidebar, text="ÂM BÁO KẾT QUẢ", font=ctk.CTkFont(size=11), progress_color=SUCCESS_COLOR)
        self.switch_sound.pack(pady=5, padx=20, anchor="w")
        self.switch_sound.select()

        self.switch_translate = ctk.CTkSwitch(self.sidebar, text="TỰ ĐỘNG DỊCH (EN->VI)", font=ctk.CTkFont(size=11), progress_color=SUCCESS_COLOR)
        self.switch_translate.pack(pady=5, padx=20, anchor="w")
        self.switch_translate.select()

        self.crawl_log = ctk.CTkTextbox(self.sidebar, height=150, font=ctk.CTkFont(size=10), fg_color="#0a0a0a", border_width=1)
        self.crawl_log.pack(padx=20, pady=5, fill="x")

        # MAIN AREA
        self.main_area = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=15, border_width=2, border_color=PRIMARY_COLOR, width=540, height=610)
        self.main_area.place(x=340, y=20); self.main_area.pack_propagate(False)
        ctk.CTkLabel(self.main_area, text="NHẬN DIỆN CHIẾN TRƯỜNG", font=ctk.CTkFont("Impact", 28), text_color=PRIMARY_COLOR).pack(pady=15)

        self.settings_frame = ctk.CTkFrame(self.main_area, fg_color="#2a2a2a", corner_radius=10); self.settings_frame.pack(padx=20, pady=10, fill="x")
        self.coord_container = ctk.CTkFrame(self.settings_frame, fg_color="transparent"); self.coord_container.pack(pady=5)
        for label, attr in [("X", "entry_x"), ("Y", "entry_y"), ("W", "entry_w"), ("H", "entry_h")]:
            f = ctk.CTkFrame(self.coord_container, fg_color="transparent"); f.pack(side="left", padx=5)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=10)).pack()
            e = ctk.CTkEntry(f, width=55, height=28, border_color=PRIMARY_COLOR, justify="center"); e.pack(); setattr(self, attr, e)
        self.btn_select_region = ctk.CTkButton(self.settings_frame, text="CHỌN VÙNG TRÊN MÀN HÌNH", fg_color="#374151", height=35); self.btn_select_region.pack(padx=20, pady=10, fill="x")

        self.res_frame = ctk.CTkFrame(self.main_area, fg_color="transparent"); self.res_frame.pack(padx=20, pady=10, fill="both", expand=True)
        ctk.CTkLabel(self.res_frame, text="CÂU HỎI NHẬN DIỆN ĐƯỢC:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaaaaa").pack(anchor="w")
        self.txt_question = ctk.CTkTextbox(self.res_frame, height=80, fg_color="#0f0f0f", border_width=1); self.txt_question.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(self.res_frame, text="ĐÁP ÁN GỢI Ý:", font=ctk.CTkFont(size=12, weight="bold"), text_color=SUCCESS_COLOR).pack(anchor="w")
        self.txt_answer = ctk.CTkTextbox(self.res_frame, height=80, fg_color="#0f0f0f", border_color=SUCCESS_COLOR, text_color=SUCCESS_COLOR, font=ctk.CTkFont(size=20, weight="bold")); self.txt_answer.pack(fill="x")

        self.status_text = ctk.CTkLabel(self.main_area, text="TRẠNG THÁI: CHỜ LỆNH", text_color="#ef4444", font=ctk.CTkFont(size=16, weight="bold")); self.status_text.pack(pady=5)
        self.btn_start = ctk.CTkButton(self.main_area, text="BẬT BOT TỰ ĐỘNG (F4)", fg_color="#b45309", hover_color="#92400e", height=55, corner_radius=10, font=ctk.CTkFont(size=20, weight="bold")); self.btn_start.pack(padx=20, pady=(0, 15), fill="x")

    def get_coords(self):
        try: return (int(self.entry_x.get()), int(self.entry_y.get()), int(self.entry_w.get()), int(self.entry_h.get()))
        except: return (0,0,0,0)

    def update_coords(self, x,y,w,h):
        for e, v in zip([self.entry_x, self.entry_y, self.entry_w, self.entry_h], [x,y,w,h]):
            e.delete(0, "end"); e.insert(0, str(v))
        self.overlay.show_region(x, y, w, h)

    def update_qa(self, q, a):
        for t in [self.txt_question, self.txt_answer]: t.configure(state="normal"); t.delete("0.0", "end")
        self.txt_question.insert("0.0", q); self.txt_answer.insert("0.0", a)
        for t in [self.txt_question, self.txt_answer]: t.configure(state="disabled")

    def update_stats(self, text): self.stats_label.configure(text=text)
    def start_selection(self, callback): RegionSelector(callback)
