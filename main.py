import time
import threading
import keyboard
import mss
import numpy as np
import pytesseract
import ctypes
import re

# Import từ project modules
from src.core.config import TESSERACT_PATH, IMAGE_UPSCALING, OCR_LANG, OCR_PSM
from src.core.db_manager import RoKDatabase
from src.gui.ui_main import RoKQuizUI
from src.logic.crawler import universal_crawler, google_search_answer
from src.utils.image_proc import preprocess_for_ocr
from src.utils.sound_manager import play_success_beep

# Thiết lập Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# FIX DPI SCALING
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

class RoKQuizController:
    def __init__(self):
        self.db = RoKDatabase()
        self.ui = RoKQuizUI()
        self.sct = mss.mss() 
        
        self.refresh_stats()
        self.scaling_factor = self.get_scaling_factor()
        self.region_selected = False
        self.bot_running = False
        self.last_question = ""
        
        # Kết nối sự kiện GUI
        self.ui.btn_start.configure(command=self.toggle_bot)
        self.ui.btn_select_region.configure(command=self.open_region_selector)
        self.ui.btn_crawl.configure(command=self.start_crawl_thread)
        keyboard.add_hotkey('f4', self.toggle_bot)
        
        # Reset ban đầu
        self.ui.update_coords(0, 0, 0, 0)
        self.ui.overlay.withdraw()

    def get_scaling_factor(self):
        try:
            user32 = ctypes.windll.user32
            screen_width_pixels = user32.GetSystemMetrics(0)
            self.ui.update()
            screen_width_logic = self.ui.winfo_screenwidth()
            return screen_width_pixels / screen_width_logic
        except: return 1.0

    def refresh_stats(self):
        stats = self.db.get_stats()
        text = "\n".join([f"{g}: {c}" for g, c in stats])
        self.ui.update_stats(f"DỮ LIỆU HIỆN CÓ:\n{text if text else 'Trống'}")

    def log_crawl(self, message):
        self.ui.crawl_log.configure(state="normal")
        self.ui.crawl_log.insert("end", f"> {message}\n")
        self.ui.crawl_log.see("end")
        self.ui.crawl_log.configure(state="disabled")

    def toggle_bot(self):
        lx, ly, lw, lh = self.ui.get_coords()
        if not self.region_selected or lw < 10 or lh < 10:
            self.open_region_selector()
            return
        self.bot_running = not self.bot_running
        if self.bot_running:
            self.ui.overlay.show_region(lx, ly, lw, lh)
            self.ui.status_text.configure(text="TRẠNG THÁI: ĐANG HOẠT ĐỘNG", text_color="#10b981")
            self.ui.btn_start.configure(text="TẮT BOT (F4)", fg_color="#dc2626")
            threading.Thread(target=self.scan_loop, daemon=True).start()
        else:
            self.ui.overlay.withdraw()
            self.ui.status_text.configure(text="TRẠNG THÁI: ĐANG TẮT", text_color="#ef4444")
            self.ui.btn_start.configure(text="BẬT BOT TỰ ĐỘNG (F4)", fg_color="#b45309")

    def open_region_selector(self):
        self.ui.withdraw()
        self.ui.overlay.withdraw()
        time.sleep(0.3)
        self.ui.start_selection(self.on_region_selected)

    def on_region_selected(self, x, y, w, h):
        self.ui.update_coords(x, y, w, h)
        self.region_selected = True
        self.ui.deiconify()
        if not self.bot_running: self.toggle_bot()

    def start_crawl_thread(self):
        url = self.ui.entry_url.get().strip()
        game = self.ui.game_option.get()
        auto_translate = self.ui.switch_translate.get()
        
        if not url:
            self.log_crawl("Vui lòng dán link web trước!")
            return
        def run():
            self.log_crawl(f"Đang cào dữ liệu {game}...")
            universal_crawler(url, game, self.db, self.log_crawl, auto_translate=auto_translate)
            self.db.export_to_csv("quiz_database.csv")
            self.refresh_stats()
        threading.Thread(target=run, daemon=True).start()

    def scan_loop(self):
        while self.bot_running:
            try:
                lx, ly, lw, lh = self.ui.get_coords()
                x, y, w, h = int(lx*self.scaling_factor), int(ly*self.scaling_factor), int(lw*self.scaling_factor), int(lh*self.scaling_factor)
                if w < 10 or h < 10: break

                monitor = {"top": y, "left": x, "width": w, "height": h}
                sct_img = self.sct.grab(monitor)
                img_np = np.array(sct_img)
                processed_img = preprocess_for_ocr(img_np, scale=IMAGE_UPSCALING)
                text = pytesseract.image_to_string(processed_img, lang=OCR_LANG, config=f'--psm {OCR_PSM}').strip()
                
                if text and len(text) > 5 and text != self.last_question:
                    self.last_question = text
                    game = self.ui.game_option.get()
                    answer = self.db.find_answer(game, text)
                    if answer:
                        self.ui.update_qa(text, answer)
                        if self.ui.switch_sound.get(): play_success_beep()
                    else:
                        self.ui.update_qa(text, "Đang tìm Google...")
                        g_ans = google_search_answer(text)
                        self.ui.update_qa(text, g_ans if g_ans else "Chưa có đáp án")
                        if g_ans and self.ui.switch_sound.get(): play_success_beep()
            except: pass
            time.sleep(0.5)

    def run(self): self.ui.mainloop()

if __name__ == "__main__":
    app = RoKQuizController()
    app.run()