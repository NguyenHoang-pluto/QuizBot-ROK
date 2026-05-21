import customtkinter as ctk
from PIL import Image, ImageDraw
import os
from src.logic.auth_manager import AuthManager

# Màu sắc chủ đạo
PRIMARY_COLOR = "#d97706" # Màu vàng gold ROK
PRIMARY_HOVER = "#b45309"
ERROR_COLOR = "#ef4444"
SUCCESS_COLOR = "#10b981"
TEXT_COLOR = "#f9fafb"

class LoginApp(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        
        self.auth = AuthManager()
        self.on_login_success = on_login_success
        
        self.title("QuizBot-ROK - Authentication")
        self.geometry("800x500")
        
        # Căn giữa cửa sổ
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"800x500+{x}+{y}")
        self.resizable(False, False)
        
        # Load và xử lý Ảnh nền (Tạo khung mờ bằng PIL)
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        bg_path = os.path.join(current_dir, "assets", "bg_login.png")
        
        if os.path.exists(bg_path):
            card_w = 380
            card_h = 360
            
            # Xử lý tạo khung kính mờ
            img = Image.open(bg_path).resize((800, 500)).convert("RGBA")
            overlay = Image.new("RGBA", (800, 500), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            x1 = (800 - card_w) // 2
            y1 = (500 - card_h) // 2
            x2 = x1 + card_w
            y2 = y1 + card_h
            
            # Vẽ hình chữ nhật bo góc với nền đen trong suốt
            draw.rounded_rectangle([x1, y1, x2, y2], radius=15, fill=(15, 23, 42, 200), outline=(51, 65, 85, 255), width=2)
            
            final_img = Image.alpha_composite(img, overlay)
            
            bg_image = ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(800, 500))
            self.lbl_bg = ctk.CTkLabel(self, image=bg_image, text="")
            self.lbl_bg.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.configure(fg_color="#0f172a")
            self.lbl_bg = self
        
        self.setup_ui()
        
    def setup_ui(self):
        # Đặt các widget TRỰC TIẾP lên lbl_bg và dùng bg_color="transparent"
        # Điều này sẽ giúp chữ và nút nổi thẳng lên nền mờ mà không bị vướng ô đen.
        
        # Logo / Tiêu đề
        self.lbl_title = ctk.CTkLabel(
            self.lbl_bg, 
            text="QUIZBOT ROK", 
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color=PRIMARY_COLOR,
            bg_color="transparent"
        )
        self.lbl_title.place(relx=0.5, rely=0.30, anchor="center")
        
        self.lbl_subtitle = ctk.CTkLabel(
            self.lbl_bg, 
            text="System Authentication", 
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#94a3b8",
            bg_color="transparent"
        )
        self.lbl_subtitle.place(relx=0.5, rely=0.38, anchor="center")
        
        # Input Field
        self.entry_key = ctk.CTkEntry(
            self.lbl_bg,
            placeholder_text="Nhập License Key...",
            font=ctk.CTkFont(family="Courier", size=15, weight="bold"),
            width=300,
            height=45,
            fg_color="#1e293b",
            border_color="#475569",
            text_color=TEXT_COLOR,
            justify="center",
            bg_color="transparent"
        )
        self.entry_key.place(relx=0.5, rely=0.53, anchor="center")
        
        # Nút Đăng nhập
        self.btn_login = ctk.CTkButton(
            self.lbl_bg,
            text="KIỂM TRA KEY",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            width=300,
            height=45,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            corner_radius=8,
            bg_color="transparent",
            command=self.process_login
        )
        self.btn_login.place(relx=0.5, rely=0.67, anchor="center")

        # Hiển thị thông báo
        self.lbl_message = ctk.CTkLabel(
            self.lbl_bg,
            text="",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=ERROR_COLOR,
            bg_color="transparent"
        )
        self.lbl_message.place(relx=0.5, rely=0.78, anchor="center")

    def process_login(self):
        key = self.entry_key.get().strip()
        if not key:
            self.lbl_message.configure(text="⚠ Vui lòng nhập License Key!", text_color=ERROR_COLOR)
            return
            
        self.btn_login.configure(state="disabled", text="ĐANG KẾT NỐI SERVER...")
        self.update()
        
        # Fake loading time for UX
        self.after(600, lambda: self._do_login(key))
        
    def _do_login(self, key):
        result = self.auth.login(key)
        
        if result['success']:
            self.lbl_message.configure(text=f"✔ {result['message']}", text_color=SUCCESS_COLOR)
            self.update()
            self.after(800, lambda: self.finish_login(result['role']))
        else:
            self.lbl_message.configure(text=f"❌ {result['message']}", text_color=ERROR_COLOR)
            self.btn_login.configure(state="normal", text="KIỂM TRA KEY")
            
    def finish_login(self, role):
        self.role_result = role
        self.quit()
