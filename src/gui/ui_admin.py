import customtkinter as ctk
import sys
from datetime import datetime
from src.logic.auth_manager import AuthManager

# ================= MÀU SẮC (Light, Dark) =================
# Thiết kế chuẩn SaaS: Nền xám nhạt, thẻ/sidebar màu trắng
BG_MAIN = ("#f1f5f9", "#0f172a")        # Nền ứng dụng chính
BG_SIDEBAR = ("#ffffff", "#1e293b")     # Thanh bên
BG_CARD = ("#ffffff", "#1e293b")        # Các hộp nội dung
BG_CARD_HOVER = ("#e2e8f0", "#334155")  # Màu khi di chuột/dòng kẻ sọc
TEXT_MAIN = ("#0f172a", "#f8fafc")      # Màu chữ chính
TEXT_MUTED = ("#64748b", "#94a3b8")     # Màu chữ phụ
PRIMARY = ("#2563eb", "#3b82f6")        # Xanh thương hiệu
SUCCESS = ("#059669", "#10b981")
WARNING = ("#d97706", "#f59e0b")
DANGER = ("#dc2626", "#ef4444")

# ================= TỪ ĐIỂN ĐA NGÔN NGỮ =================
I18N = {
    "vi": {
        "title": "QuizBot-ROK - Không gian Quản trị",
        "menu_dash": "📊  Tổng quan",
        "menu_keys": "🔑  Quản lý Key",
        "menu_set": "⚙️  Cài đặt",
        "menu_logout": "🚪  Đăng xuất",
        "dash_title": "Tổng quan hệ thống",
        "stat_total": "Tổng số Key",
        "stat_active": "Đang hoạt động",
        "stat_ban": "Bị khóa",
        "stat_rev": "Tổng Doanh Thu (VNĐ)",
        "key_title": "Danh sách License Keys",
        "search_ph": "🔍 Tìm kiếm mã key...",
        "btn_refresh": "🔄 Làm mới",
        "create_lbl": "Tạo Key Mới:",
        "price_lbl": "Giá bán (VNĐ):",
        "dur_1": "1 Ngày",
        "dur_7": "7 Ngày",
        "dur_30": "30 Ngày",
        "dur_life": "Vĩnh viễn",
        "btn_create": "+ TẠO KEY",
        "col_key": "Mã Key",
        "col_stat": "Trạng thái",
        "col_exp": "Hạn sử dụng",
        "col_hwid": "Thiết bị (HWID)",
        "col_act": "Hành động",
        "st_locked": "🔒 Đã khóa thiết bị",
        "st_unlocked": "🔓 Chưa sử dụng",
        "st_life": "Vĩnh viễn",
        "btn_cp": "Copy",
        "btn_unbind": "Gỡ HWID",
        "btn_ban": "Khóa",
        "btn_unban": "Mở khóa",
        "msg_copy": "Đã copy vào Clipboard!",
        "msg_err": "Lỗi hệ thống",
        "msg_notfound": "Không tìm thấy dữ liệu.",
        "set_title": "Cài đặt Hệ thống",
        "set_theme": "Giao diện (Sáng / Tối):",
        "set_lang": "Ngôn ngữ hệ thống:"
    },
    "en": {
        "title": "QuizBot-ROK - Admin Workspace",
        "menu_dash": "📊  Dashboard",
        "menu_keys": "🔑  Manage Keys",
        "menu_set": "⚙️  Settings",
        "menu_logout": "🚪  Logout",
        "dash_title": "System Overview",
        "stat_total": "Total Keys",
        "stat_active": "Active",
        "stat_ban": "Banned",
        "stat_rev": "Total Revenue (VND)",
        "key_title": "License Keys List",
        "search_ph": "🔍 Search license keys...",
        "btn_refresh": "🔄 Refresh",
        "create_lbl": "Create New Key:",
        "price_lbl": "Price (VND):",
        "dur_1": "1 Day",
        "dur_7": "7 Days",
        "dur_30": "30 Days",
        "dur_life": "Lifetime",
        "btn_create": "+ CREATE",
        "col_key": "Key Code",
        "col_stat": "Status",
        "col_exp": "Expiration",
        "col_hwid": "Device (HWID)",
        "col_act": "Actions",
        "st_locked": "🔒 Device Locked",
        "st_unlocked": "🔓 Unused",
        "st_life": "Lifetime",
        "btn_cp": "Copy",
        "btn_unbind": "Unbind",
        "btn_ban": "Ban",
        "btn_unban": "Unban",
        "msg_copy": "Copied to Clipboard!",
        "msg_err": "System Error",
        "msg_notfound": "No records found.",
        "set_title": "System Settings",
        "set_theme": "Appearance Theme:",
        "set_lang": "System Language:"
    }
}

class AdminDashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.auth = AuthManager()
        
        # State
        self.lang = "vi"
        self.theme = "Dark"
        ctk.set_appearance_mode(self.theme)
        
        self.geometry("1150x650")
        self.minsize(950, 600)
        self.configure(fg_color=BG_MAIN)
        
        # Center Window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1150 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"1150x650+{x}+{y}")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_frame = None
        self.frames = {}
        
        self.setup_sidebar()
        self.setup_dashboard_frame()
        self.setup_keys_frame()
        self.setup_settings_frame()
        
        self.apply_translations()
        self.show_frame("dashboard")

    def t(self, key):
        return I18N[self.lang].get(key, key)

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0, width=220)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) 
        
        self.lbl_logo = ctk.CTkLabel(self.sidebar_frame, text="👑 ROK ADMIN", font=ctk.CTkFont("Inter", 22, "bold"), text_color=PRIMARY)
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(30, 40))
        
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, anchor="w", fg_color="transparent", text_color=TEXT_MAIN, hover_color=BG_CARD_HOVER, font=ctk.CTkFont("Inter", 15), height=40, command=lambda: self.show_frame("dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_keys = ctk.CTkButton(self.sidebar_frame, anchor="w", fg_color="transparent", text_color=TEXT_MAIN, hover_color=BG_CARD_HOVER, font=ctk.CTkFont("Inter", 15), height=40, command=lambda: self.show_frame("keys"))
        self.btn_keys.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_settings = ctk.CTkButton(self.sidebar_frame, anchor="w", fg_color="transparent", text_color=TEXT_MAIN, hover_color=BG_CARD_HOVER, font=ctk.CTkFont("Inter", 15), height=40, command=lambda: self.show_frame("settings"))
        self.btn_settings.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_logout = ctk.CTkButton(self.sidebar_frame, anchor="w", fg_color="transparent", text_color=DANGER, hover_color=BG_CARD_HOVER, font=ctk.CTkFont("Inter", 15), height=40, command=self.logout)
        self.btn_logout.grid(row=6, column=0, padx=10, pady=20, sticky="ew")

    def highlight_menu(self, frame_name):
        self.btn_dashboard.configure(fg_color="transparent")
        self.btn_keys.configure(fg_color="transparent")
        self.btn_settings.configure(fg_color="transparent")
        
        if frame_name == "dashboard":
            self.btn_dashboard.configure(fg_color=PRIMARY)
        elif frame_name == "keys":
            self.btn_keys.configure(fg_color=PRIMARY)
        elif frame_name == "settings":
            self.btn_settings.configure(fg_color=PRIMARY)

    def show_frame(self, frame_name):
        self.highlight_menu(frame_name)
        if self.current_frame:
            self.current_frame.grid_forget()
            
        frame = self.frames[frame_name]
        frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.current_frame = frame
        
        if frame_name == "dashboard":
            self.refresh_dashboard()
        elif frame_name == "keys":
            self.refresh_keys_data()

    # ========================== DASHBOARD ==========================
    def setup_dashboard_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.lbl_dash_title = ctk.CTkLabel(frame, font=ctk.CTkFont("Inter", 26, "bold"), text_color=TEXT_MAIN)
        self.lbl_dash_title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 30))
        
        self.lbl_stat_total, self.val_total = self.create_stat_card(frame, PRIMARY, 0)
        self.lbl_stat_active, self.val_active = self.create_stat_card(frame, SUCCESS, 1)
        self.lbl_stat_banned, self.val_banned = self.create_stat_card(frame, DANGER, 2)
        self.lbl_stat_rev, self.val_rev = self.create_stat_card(frame, WARNING, 3)
        
        # Biểu đồ (Charts Area)
        self.chart_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.chart_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=20)
        self.chart_frame.grid_columnconfigure((0, 1), weight=1)
        self.chart_frame.grid_rowconfigure(0, weight=1)
        
        frame.grid_rowconfigure(2, weight=1) # Allow charts to expand
        
        self.frames["dashboard"] = frame
        
    def create_stat_card(self, parent, color, col):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12, height=120)
        card.grid(row=1, column=col, sticky="ew", padx=10)
        card.pack_propagate(False)
        
        lbl_title = ctk.CTkLabel(card, font=ctk.CTkFont("Inter", 14), text_color=TEXT_MUTED)
        lbl_title.pack(anchor="w", padx=20, pady=(20, 0))
        lbl_val = ctk.CTkLabel(card, text="0", font=ctk.CTkFont("Inter", 36, "bold"), text_color=color)
        lbl_val.pack(anchor="w", padx=20)
        
        return lbl_title, lbl_val

    def format_money(self, amount):
        return f"{amount:,.0f}".replace(",", ".")
        
    def refresh_dashboard(self):
        stats = self.auth.db.get_stats()
        self.val_total.configure(text=str(stats['total']))
        self.val_active.configure(text=str(stats['active']))
        self.val_banned.configure(text=str(stats['banned']))
        self.val_rev.configure(text=self.format_money(stats['revenue']))
        self.draw_charts(stats)

    def draw_charts(self, stats):
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.pyplot as plt
            
            # Clear old charts
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
                
            # Cấu hình màu nền đồ thị theo theme
            is_dark = self.theme == "Dark"
            bg_hex = "#1e293b" if is_dark else "#ffffff"
            text_hex = "#f8fafc" if is_dark else "#0f172a"
            
            plt.rcParams.update({'text.color': text_hex, 'axes.labelcolor': text_hex, 
                                 'xtick.color': text_hex, 'ytick.color': text_hex})
            
            # 1. Biểu đồ tròn (Trạng thái Key)
            fig1, ax1 = plt.subplots(figsize=(4, 4), dpi=100)
            fig1.patch.set_facecolor(bg_hex)
            ax1.set_facecolor(bg_hex)
            
            labels = ['Active', 'Banned']
            sizes = [stats['active'], stats['banned']]
            colors = ['#10b981', '#ef4444']
            
            if sum(sizes) == 0:
                sizes = [1, 0] # Tránh lỗi chia cho 0
                
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            ax1.set_title("Trạng thái Key (Key Status)", color=text_hex)
            
            canvas1 = FigureCanvasTkAgg(fig1, self.chart_frame)
            canvas1.draw()
            widget1 = canvas1.get_tk_widget()
            widget1.grid(row=0, column=0, sticky="nsew", padx=10)
            
            # 2. Biểu đồ cột (Doanh thu theo gói - Dữ liệu giả định tạm thời)
            fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=100)
            fig2.patch.set_facecolor(bg_hex)
            ax2.set_facecolor(bg_hex)
            
            # Đọc doanh thu thực tế từ CSDL
            keys = self.auth.db.get_all_keys()
            rev_1d = sum(k['price'] for k in keys if k['expires_at'] and (k['expires_at'] - k['created_at']).days <= 1)
            rev_7d = sum(k['price'] for k in keys if k['expires_at'] and 1 < (k['expires_at'] - k['created_at']).days <= 7)
            rev_30d = sum(k['price'] for k in keys if k['expires_at'] and 7 < (k['expires_at'] - k['created_at']).days <= 30)
            rev_life = sum(k['price'] for k in keys if not k['expires_at'])
            
            packages = ['1 Day', '7 Days', '30 Days', 'Lifetime']
            revenues = [rev_1d, rev_7d, rev_30d, rev_life]
            
            ax2.bar(packages, revenues, color='#3b82f6')
            ax2.set_title("Doanh thu theo Gói (Revenue by Package)", color=text_hex)
            ax2.ticklabel_format(style='plain', axis='y') # Tắt format khoa học (1e6)
            
            canvas2 = FigureCanvasTkAgg(fig2, self.chart_frame)
            canvas2.draw()
            widget2 = canvas2.get_tk_widget()
            widget2.grid(row=0, column=1, sticky="nsew", padx=10)
            
        except Exception as e:
            print(f"Lỗi vẽ biểu đồ: {e}")

    # ========================== QUẢN LÝ KEY ==========================
    def setup_keys_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_columnconfigure(0, weight=1)
        
        self.lbl_key_title = ctk.CTkLabel(toolbar, font=ctk.CTkFont("Inter", 22, "bold"), text_color=TEXT_MAIN)
        self.lbl_key_title.grid(row=0, column=0, sticky="w")
        
        self.entry_search = ctk.CTkEntry(toolbar, width=250, height=35)
        self.entry_search.grid(row=0, column=1, padx=10)
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_keys())
        
        self.btn_refresh = ctk.CTkButton(toolbar, width=100, height=35, fg_color=BG_CARD, hover_color=BG_CARD_HOVER, text_color=TEXT_MAIN, command=self.refresh_keys_data)
        self.btn_refresh.grid(row=0, column=2, padx=5)
        
        create_frame = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=8, height=60)
        create_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        self.lbl_create = ctk.CTkLabel(create_frame, font=ctk.CTkFont(weight="bold"), text_color=TEXT_MAIN)
        self.lbl_create.pack(side="left", padx=20)
        
        self.duration_var = ctk.StringVar(value="30")
        self.rb_dur1 = ctk.CTkRadioButton(create_frame, variable=self.duration_var, value="1", text_color=TEXT_MAIN, command=self.update_price_hint)
        self.rb_dur7 = ctk.CTkRadioButton(create_frame, variable=self.duration_var, value="7", text_color=TEXT_MAIN, command=self.update_price_hint)
        self.rb_dur30 = ctk.CTkRadioButton(create_frame, variable=self.duration_var, value="30", text_color=TEXT_MAIN, command=self.update_price_hint)
        self.rb_life = ctk.CTkRadioButton(create_frame, variable=self.duration_var, value="", text_color=TEXT_MAIN, command=self.update_price_hint)
        for rb in [self.rb_dur1, self.rb_dur7, self.rb_dur30, self.rb_life]:
            rb.pack(side="left", padx=10)
            
        # Price Entry
        self.lbl_price = ctk.CTkLabel(create_frame, text="Giá (VNĐ):", font=ctk.CTkFont(weight="bold"), text_color=TEXT_MAIN)
        self.lbl_price.pack(side="left", padx=(20, 5))
        self.entry_price = ctk.CTkEntry(create_frame, width=90, height=30)
        self.entry_price.pack(side="left")
        self.entry_price.insert(0, "150000") # Default for 30 days
            
        self.btn_create = ctk.CTkButton(create_frame, width=120, fg_color=SUCCESS, hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=self.create_new_key)
        self.btn_create.pack(side="right", padx=20, pady=15)
        
        self.lbl_create_status = ctk.CTkLabel(create_frame, text="", text_color=SUCCESS)
        self.lbl_create_status.pack(side="right", padx=10)
        
        self.table_bg = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=8)
        self.table_bg.grid(row=2, column=0, sticky="nsew")
        
        self.header = ctk.CTkFrame(self.table_bg, fg_color="transparent", height=40)
        self.header.pack(fill="x", padx=10, pady=5)
        
        self.lbl_cols = []
        widths = [250, 100, 150, 150, 200]
        for w in widths:
            lbl = ctk.CTkLabel(self.header, font=ctk.CTkFont("Inter", 13, "bold"), text_color=TEXT_MUTED)
            lbl.pack(side="left", padx=10)
            if w == 200:
                lbl.pack_configure(side="right")
            self.lbl_cols.append(lbl)
        
        ctk.CTkFrame(self.table_bg, height=1, fg_color=TEXT_MUTED).pack(fill="x", padx=10)
        
        self.scroll_table = ctk.CTkScrollableFrame(self.table_bg, fg_color="transparent")
        self.scroll_table.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.frames["keys"] = frame
        self.all_keys_cache = []

    def refresh_keys_data(self):
        self.all_keys_cache = self.auth.db.get_all_keys()
        self.filter_keys()
        
    def filter_keys(self):
        query = self.entry_search.get().strip().lower()
        
        for widget in self.scroll_table.winfo_children():
            widget.destroy()
            
        filtered = [k for k in self.all_keys_cache if query in k['key_code'].lower()]
        
        if not filtered:
            ctk.CTkLabel(self.scroll_table, text=self.t("msg_notfound"), text_color=TEXT_MUTED).pack(pady=40)
            return
            
        for idx, key_info in enumerate(filtered):
            bg = "transparent" if idx % 2 == 0 else BG_CARD_HOVER
            self.create_table_row(key_info, bg)

    def create_table_row(self, key_info, bg_color):
        row = ctk.CTkFrame(self.scroll_table, fg_color=bg_color, height=45, corner_radius=4)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        
        code = key_info['key_code']
        status = key_info['status']
        hwid = self.t("st_locked") if key_info['hwid'] else self.t("st_unlocked")
        
        if not key_info['expires_at']:
            exp = self.t("st_life")
        else:
            exp_date = key_info['expires_at']
            exp = exp_date.strftime("%d/%m/%Y")
            if (exp_date - datetime.now()).days < 3 and status == 'active':
                exp += " ⚠️"
        
        color_status = SUCCESS if status == 'active' else DANGER
        
        ctk.CTkLabel(row, text=code, font=ctk.CTkFont("Courier", 13, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=status.upper(), text_color=color_status, width=100, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(row, text=exp, width=150, anchor="w", text_color=TEXT_MAIN).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=hwid, text_color=TEXT_MUTED, width=150, anchor="w").pack(side="left", padx=10)
        
        btn_copy = ctk.CTkButton(row, text=self.t("btn_cp"), width=50, height=26, fg_color=TEXT_MUTED, hover_color="#374151", command=lambda: self.clipboard_append(code))
        btn_copy.pack(side="right", padx=5, pady=9)
        
        if key_info['hwid']:
            btn_reset = ctk.CTkButton(row, text=self.t("btn_unbind"), width=70, height=26, fg_color=WARNING, hover_color="#d97706", command=lambda: self.action_reset_hwid(code))
            btn_reset.pack(side="right", padx=5, pady=9)
            
        is_active = (status == 'active')
        btn_ban = ctk.CTkButton(
            row, 
            text=self.t("btn_ban") if is_active else self.t("btn_unban"), 
            width=60, height=26, 
            fg_color=DANGER if is_active else SUCCESS, 
            hover_color="#b91c1c" if is_active else "#059669", 
            command=lambda: self.action_toggle_ban(code, status)
        )
        btn_ban.pack(side="right", padx=5, pady=9)

    def update_price_hint(self):
        val = self.duration_var.get()
        prices = {"1": "10000", "7": "50000", "30": "150000", "": "500000"}
        self.entry_price.delete(0, 'end')
        self.entry_price.insert(0, prices.get(val, "0"))

    def create_new_key(self):
        val = self.duration_var.get()
        duration = int(val) if val else None
        
        try:
            price_val = int(self.entry_price.get() or "0")
        except ValueError:
            price_val = 0
            
        new_key = self.auth.generate_key(duration_days=duration, price=price_val)
        if new_key:
            self.clipboard_clear()
            self.clipboard_append(new_key)
            self.lbl_create_status.configure(text=self.t("msg_copy"), text_color=SUCCESS)
            self.refresh_keys_data()
            self.after(3000, lambda: self.lbl_create_status.configure(text=""))
        else:
            self.lbl_create_status.configure(text=self.t("msg_err"), text_color=DANGER)

    def action_reset_hwid(self, code):
        if self.auth.db.reset_key_hwid(code): self.refresh_keys_data()
            
    def action_toggle_ban(self, code, current_status):
        new_status = 'banned' if current_status == 'active' else 'active'
        if self.auth.db.update_key_status(code, new_status): self.refresh_keys_data()

    # ========================== SETTINGS ==========================
    def setup_settings_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.lbl_set_title = ctk.CTkLabel(frame, font=ctk.CTkFont("Inter", 26, "bold"), text_color=TEXT_MAIN)
        self.lbl_set_title.pack(anchor="w", pady=(0, 30))
        
        card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12)
        card.pack(fill="x", pady=10)
        
        # Theme Toggle
        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=20)
        self.lbl_set_theme = ctk.CTkLabel(row1, font=ctk.CTkFont("Inter", 15), text_color=TEXT_MAIN)
        self.lbl_set_theme.pack(side="left")
        
        self.sw_theme = ctk.CTkSwitch(row1, text="Dark Mode", command=self.toggle_theme)
        self.sw_theme.select()
        self.sw_theme.pack(side="right")
        
        # Language Select
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=20)
        self.lbl_set_lang = ctk.CTkLabel(row2, font=ctk.CTkFont("Inter", 15), text_color=TEXT_MAIN)
        self.lbl_set_lang.pack(side="left")
        
        self.cb_lang = ctk.CTkOptionMenu(row2, values=["Tiếng Việt", "English"], command=self.change_language)
        self.cb_lang.pack(side="right")
        
        self.frames["settings"] = frame

    def toggle_theme(self):
        self.theme = "Dark" if self.sw_theme.get() == 1 else "Light"
        ctk.set_appearance_mode(self.theme)
        self.sw_theme.configure(text="Dark Mode" if self.theme == "Dark" else "Light Mode")

    def change_language(self, choice):
        self.lang = "vi" if choice == "Tiếng Việt" else "en"
        self.apply_translations()
        if self.current_frame == self.frames["keys"]:
            self.refresh_keys_data() # Update table texts

    def apply_translations(self):
        self.title(self.t("title"))
        
        # Sidebar
        self.btn_dashboard.configure(text=self.t("menu_dash"))
        self.btn_keys.configure(text=self.t("menu_keys"))
        self.btn_settings.configure(text=self.t("menu_set"))
        self.btn_logout.configure(text=self.t("menu_logout"))
        
        # Dashboard
        self.lbl_dash_title.configure(text=self.t("dash_title"))
        self.lbl_stat_total.configure(text=self.t("stat_total"))
        self.lbl_stat_active.configure(text=self.t("stat_active"))
        self.lbl_stat_banned.configure(text=self.t("stat_ban"))
        self.lbl_stat_rev.configure(text=self.t("stat_rev"))
        
        # Keys
        self.lbl_key_title.configure(text=self.t("key_title"))
        self.entry_search.configure(placeholder_text=self.t("search_ph"))
        self.btn_refresh.configure(text=self.t("btn_refresh"))
        self.lbl_create.configure(text=self.t("create_lbl"))
        self.lbl_price.configure(text=self.t("price_lbl"))
        self.rb_dur1.configure(text=self.t("dur_1"))
        self.rb_dur7.configure(text=self.t("dur_7"))
        self.rb_dur30.configure(text=self.t("dur_30"))
        self.rb_life.configure(text=self.t("dur_life"))
        self.btn_create.configure(text=self.t("btn_create"))
        
        col_names = [self.t("col_key"), self.t("col_stat"), self.t("col_exp"), self.t("col_hwid"), self.t("col_act")]
        for lbl, name in zip(self.lbl_cols, col_names):
            lbl.configure(text=name)
            
        # Settings
        self.lbl_set_title.configure(text=self.t("set_title"))
        self.lbl_set_theme.configure(text=self.t("set_theme"))
        self.lbl_set_lang.configure(text=self.t("set_lang"))

    def logout(self):
        self.destroy()
        import subprocess
        subprocess.Popen([sys.executable, "main.py"])

if __name__ == "__main__":
    app = AdminDashboardApp()
    app.mainloop()
