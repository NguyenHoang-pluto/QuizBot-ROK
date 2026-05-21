import time
import threading
import keyboard
import mss
import numpy as np
import pytesseract
import ctypes
import re

# Import từ project modules
from difflib import SequenceMatcher
from src.core.config import TESSERACT_PATH, IMAGE_UPSCALING, OCR_LANG, OCR_PSM
from src.core.db_manager import RoKDatabase
from src.gui.ui_main import RoKQuizUI, PRIMARY_COLOR, SUCCESS_COLOR
from src.logic.crawler import universal_crawler, google_search_answer, google_and_wiki_corpus
from src.utils.image_proc import preprocess_for_ocr, preprocess_option_for_ocr
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
        self.sct = mss.MSS() 
        
        self.refresh_stats()
        self.scaling_factor = self.get_scaling_factor()
        self.region_selected = False
        self.bot_running = False
        self.last_question = ""
        
        # Kết nối sự kiện GUI
        self.ui.btn_start.configure(command=self.toggle_bot)
        self.ui.btn_start_compact.configure(command=self.toggle_bot)
        self.ui.btn_select_q.configure(command=self.open_region_selector_q)
        self.ui.btn_select_opts.configure(command=self.open_region_selector_opts)
        self.ui.btn_crawl.configure(command=self.start_crawl_thread)
        self.ui.btn_save_db.configure(command=self.save_current_qa_to_db)
        self.ui.btn_save_db_compact.configure(command=self.save_current_qa_to_db)
        keyboard.add_hotkey('f4', self.toggle_bot)
        
        # Reset ban đầu
        self.ui.update_coords_q(0, 0, 0, 0)
        self.ui.update_coords_opts(0, 0, 0, 0)
        self.ui.overlay_q.withdraw()
        self.ui.overlay_opts.withdraw()

    def extract_clean_db_answer(self, a):
        if not a: return ""
        # Nếu có tiền tố [Gợi ý 80%]: ... hoặc tương tự
        match_gui = re.search(r'\[Gợi ý\s+\d+%.*?\]:\s*(.*?)(?:\n|$)', a)
        if match_gui:
            return match_gui.group(1).strip()
            
        for line in a.split("\n"):
            if "⭐" in line or "💡" in line or "✅" in line:
                # Thử tìm dạng [A] Option <==
                match = re.search(r'\[[A-Da-d]\]\s*(.*?)(?:\s*<==|\n|$)', line)
                if match:
                    return match.group(1).strip()
                # Thử tìm dạng ✅ ĐÁP ÁN TRONG DB: Option
                match_db = re.search(r'✅\s*(?:ĐÁP ÁN TRONG DB|ĐÁP ÁN TRONG DB \(Không khớp\))\s*:\s*(.*)', line)
                if match_db:
                    return match_db.group(1).strip()
        return a

    def save_current_qa_to_db(self):
        # Lấy văn bản từ chế độ hiện tại (Đầy đủ hoặc Thu nhỏ)
        if self.ui.is_compact:
            q = self.ui.txt_question_compact.get("0.0", "end").strip()
            a = self.ui.txt_answer_compact.get("0.0", "end").strip()
        else:
            q = self.ui.txt_question.get("0.0", "end").strip()
            a = self.ui.txt_answer.get("0.0", "end").strip()
            
        if not q or q == "Đang đợi câu hỏi..." or not a or a in ["CHƯA CÓ KẾT QUẢ", "Chưa có đáp án", "Đang tìm Google..."]:
            # Hiển thị lỗi trên thanh trạng thái
            old_text = self.ui.status_text.cget("text")
            old_color = self.ui.status_text.cget("text_color")
            self.ui.status_text.configure(text="LỖI: CHƯA CÓ DỮ LIỆU ĐỂ LƯU!", text_color="#dc2626")
            self.ui.after(2000, lambda: self.ui.status_text.configure(text=old_text, text_color=old_color))
            return
            
        clean_a = self.extract_clean_db_answer(a)
        game = self.ui.game_option.get()
        success = self.db.save_or_update_question(game, q, clean_a)
        if success:
            # Tự động xuất CSV mới
            self.db.export_to_csv("data/quiz_database.csv")
            self.refresh_stats()
            
            # Đồng bộ lại nội dung HUD
            self.ui.hud.update_hud(q, a)
            
            # Thông báo thành công lên thanh trạng thái trong 2 giây
            old_text = self.ui.status_text.cget("text")
            old_color = self.ui.status_text.cget("text_color")
            self.ui.status_text.configure(text="💾 ĐÃ LƯU THÀNH CÔNG VÀO DATABASE & CSV!", text_color="#10b981")
            self.ui.after(2000, lambda: self.ui.status_text.configure(text=old_text, text_color=old_color))

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
        self.ui.after(0, lambda: self.ui.update_stats(f"DỮ LIỆU HIỆN CÓ:\n{text if text else 'Trống'}"))

    def log_crawl(self, message):
        def update_log():
            self.ui.crawl_log.configure(state="normal")
            self.ui.crawl_log.insert("end", f"> {message}\n")
            self.ui.crawl_log.see("end")
            self.ui.crawl_log.configure(state="disabled")
        self.ui.after(0, update_log)

    def toggle_bot(self):
        qx, qy, qw, qh = self.ui.get_coords_q()
        ox, oy, ow, oh = self.ui.get_coords_opts()
        if qw < 10 or qh < 10:
            self.open_region_selector_q()
            return
        if ow < 10 or oh < 10:
            self.open_region_selector_opts()
            return
        self.bot_running = not self.bot_running
        if self.bot_running:
            self.ui.overlay_q.set_scan_mode(True)
            self.ui.overlay_opts.set_scan_mode(True)
            self.ui.overlay_q.show_region(qx, qy, qw, qh)
            self.ui.overlay_opts.show_region(ox, oy, ow, oh)
            try:
                if self.ui.switch_hud.get():
                    # Đặt HUD ở góc trên trái màn hình để không che vùng quét game
                    self.ui.hud.geometry("+10+10")
                    self.ui.hud.deiconify()
            except Exception as e:
                print(f"[HUD ERROR]: {e}")
            self.ui.status_text.configure(text="TRẠNG THÁI: ĐANG HOẠT ĐỘNG", text_color="#10b981")
            self.ui.btn_start.configure(text="TẮT BOT (F4)", fg_color="#dc2626")
            self.ui.btn_start_compact.configure(text="TẮT BOT (F4)", fg_color="#dc2626")
            # Thu nhỏ app xuống taskbar - chỉ giữ HUD + Overlay trong suốt
            self.ui.iconify()
            threading.Thread(target=self.scan_loop, daemon=True).start()
        else:
            self.ui.overlay_q.set_scan_mode(False)
            self.ui.overlay_opts.set_scan_mode(False)
            self.ui.overlay_q.withdraw()
            self.ui.overlay_opts.withdraw()
            self.ui.hud.withdraw()
            # Khôi phục app từ taskbar
            self.ui.deiconify()
            self.ui.status_text.configure(text="TRẠNG THÁI: ĐANG TẮT", text_color="#ef4444")
            self.ui.btn_start.configure(text="BẬT BOT TỰ ĐỘNG (F4)", fg_color="#b45309")
            self.ui.btn_start_compact.configure(text="BẬT BOT (F4)", fg_color="#b45309")

    def open_region_selector_q(self):
        self.ui.withdraw()
        self.ui.overlay_q.withdraw()
        self.ui.overlay_opts.withdraw()
        time.sleep(0.3)
        self.ui.start_selection(self.on_region_q_selected, mode="question")

    def on_region_q_selected(self, x, y, w, h):
        self.ui.update_coords_q(x, y, w, h)
        self.region_selected = True
        self.ui.deiconify()
        self.ui.overlay_q.show_region(x, y, w, h)

    def open_region_selector_opts(self):
        self.ui.withdraw()
        self.ui.overlay_q.withdraw()
        self.ui.overlay_opts.withdraw()
        time.sleep(0.3)
        self.ui.start_selection(self.on_region_opts_selected, mode="options")

    def on_region_opts_selected(self, x, y, w, h):
        self.ui.update_coords_opts(x, y, w, h)
        self.ui.deiconify()
        self.ui.overlay_opts.show_region(x, y, w, h)

    def start_crawl_thread(self):
        url = self.ui.entry_url.get().strip()
        game = self.ui.game_option.get()
        auto_translate = self.ui.switch_translate.get()
        
        if not url:
            self.log_crawl("Vui lòng dán link web trước!")
            return
            
        # Reset thanh tiến độ và nhãn hiển thị trước khi chạy
        self.ui.crawl_progress.set(0)
        self.ui.lbl_crawl_progress.configure(text="Tiến độ: Đang kết nối...", text_color=PRIMARY_COLOR)
        
        def progress_cb(current, total, added):
            def update_gui():
                pct = int((current / total) * 100) if total > 0 else 0
                self.ui.crawl_progress.set(current / total if total > 0 else 0)
                self.ui.lbl_crawl_progress.configure(
                    text=f"Tiến độ: {pct}% ({current}/{total}) - Đã thêm: {added}",
                    text_color=SUCCESS_COLOR if current == total else PRIMARY_COLOR
                )
            self.ui.after(0, update_gui)
            
        def run():
            self.log_crawl(f"Đang cào dữ liệu {game}...")
            universal_crawler(
                url, 
                game, 
                self.db, 
                self.log_crawl, 
                auto_translate=auto_translate,
                progress_callback=progress_cb
            )
            self.db.export_to_csv("data/quiz_database.csv")
            self.refresh_stats()
            
        threading.Thread(target=run, daemon=True).start()

    def match_and_analyze(self, game, question, options):
        """
        So sánh đáp án trong DB với các đáp án quét được hoặc chạy phân tích co-occurrence tần suất online.
        """
        # 1. Tìm trong Database
        db_answer = self.db.find_answer(game, question)
        
        letters = ["A", "B", "C", "D"]
        
        if db_answer:
            # Lấy đáp án sạch từ DB để so khớp
            clean_db_ans = self.extract_clean_db_answer(db_answer)
            if not clean_db_ans:
                clean_db_ans = db_answer
                
            norm_db = self.db.normalize_text(clean_db_ans)
            
            best_idx = -1
            best_score = 0.0
            
            for idx, opt in enumerate(options):
                if not opt: continue
                norm_opt = self.db.normalize_text(opt)
                score = SequenceMatcher(None, norm_db, norm_opt).ratio()
                if score > best_score:
                    best_score = score
                    best_idx = idx
            
            # Nếu tìm thấy đáp án khớp cao (trên 60%)
            if best_score > 0.6 and best_idx != -1:
                formatted_lines = []
                pct = int(best_score * 100)
                for idx, opt in enumerate(options):
                    opt_str = opt if opt else "(Không quét được)"
                    if idx == best_idx:
                        formatted_lines.append(f"⭐ [{letters[idx]}] {opt_str} <== ĐÁP ÁN KHỚP DB ({pct}%)")
                    else:
                        formatted_lines.append(f"   [{letters[idx]}] {opt_str}")
                return "\n".join(formatted_lines), True
            else:
                # Nếu không khớp với đáp án nào trong 4 đáp án
                formatted_lines = []
                for idx, opt in enumerate(options):
                    opt_str = opt if opt else "(Không quét được)"
                    formatted_lines.append(f"   [{letters[idx]}] {opt_str}")
                formatted_lines.append(f"\n✅ ĐÁP ÁN TRONG DB (Không khớp): {db_answer}")
                return "\n".join(formatted_lines), True

        # 2. Nếu CHƯA có câu hỏi trong database -> Tiến hành phân tích Co-occurrence
        corpus = google_and_wiki_corpus(question)
        if not corpus:
            formatted_lines = []
            for idx, opt in enumerate(options):
                opt_str = opt if opt else "(Không quét được)"
                formatted_lines.append(f"   [{letters[idx]}] {opt_str}")
            formatted_lines.append("\n💡 GỢI Ý ONLINE: Không tìm thấy tài liệu tìm kiếm trực tuyến.")
            return "\n".join(formatted_lines), False
            
        norm_corpus = self.db.normalize_text(corpus)
        norm_options = [self.db.normalize_text(opt) for opt in options]
        
        # Danh sách Stop Words tiếng Việt & tiếng Anh phổ biến
        STOP_WORDS = {
            'ai', 'la', 'nguoi', 'cua', 'trong', 'co', 'bao', 'nhieu', 'nao', 'sau', 'day', 'khong', 'thi', 
            'va', 'de', 'duoc', 'mot', 'nhung', 'cac', 'o', 'da', 'tung', 'lam', 'ra', 'tai', 'boi', 'cho', 
            'biet', 'vi', 'the', 'nao', 'gi', 'dau', 'the', 'nao', 'truoc', 'sau', 'chinh', 'thuc',
            'who', 'is', 'the', 'of', 'in', 'has', 'how', 'many', 'which', 'following', 'not', 'then', 
            'and', 'to', 'be', 'a', 'some', 'these', 'at', 'by', 'for', 'know', 'why', 'what', 'where',
            'first', 'second', 'third'
        }
        
        # Thống kê tần suất từ trong các options để lọc các từ chung
        word_counts = {}
        non_empty_opts = [opt for opt in norm_options if opt]
        for opt in non_empty_opts:
            words = set(opt.split())
            for w in words:
                if len(w) > 1 and w not in STOP_WORDS:
                    word_counts[w] = word_counts.get(w, 0) + 1
                    
        # Loại trừ các từ xuất hiện ở hầu hết các đáp án (ví dụ xuất hiện ở >= 2 đáp án nếu có >= 2 đáp án)
        exclude_words = set()
        if len(non_empty_opts) >= 2:
            exclude_words = {w for w, count in word_counts.items() if count >= max(2, len(non_empty_opts))}
            
        # Tính điểm cho từng đáp án
        scores = [0] * 4
        for idx, opt in enumerate(norm_options):
            if not opt: continue
            
            # Tier 1: Khớp nguyên cụm từ (Exact phrase matching)
            exact_matches = norm_corpus.count(opt)
            scores[idx] += exact_matches * 15
            
            # Tier 2: Khớp từng từ đơn lẻ đặc trưng
            words = [w for w in opt.split() if len(w) > 1 and w not in STOP_WORDS and w not in exclude_words]
            word_hits = 0
            for w in words:
                w_count = norm_corpus.count(w)
                scores[idx] += w_count * 2
                if w_count > 0:
                    word_hits += 1
                    
            # Thêm điểm cộng nếu khớp toàn bộ từ trong đáp án
            if words and word_hits == len(words):
                scores[idx] += 5
                
        # Tìm đáp án có điểm cao nhất
        max_score = max(scores)
        best_idx = -1
        if max_score > 0:
            best_idx = scores.index(max_score)
            
        formatted_lines = []
        for idx, opt in enumerate(options):
            opt_str = opt if opt else "(Không quét được)"
            if max_score > 0 and idx == best_idx:
                formatted_lines.append(f"💡 [{letters[idx]}] {opt_str} <== GỢI Ý ONLINE (Điểm: {scores[idx]})")
            else:
                score_str = f" (Điểm: {scores[idx]})" if opt else ""
                formatted_lines.append(f"   [{letters[idx]}] {opt_str}{score_str}")
                
        if max_score == 0:
            # Fallback nếu không trùng khớp đáp án nào
            # Lấy snippet đầu của corpus để gợi ý
            snippet = corpus[:150].replace("\n", " ") + "..."
            formatted_lines.append(f"\n💡 GỢI Ý ONLINE (Không khớp đáp án nào): {snippet}")
            
        return "\n".join(formatted_lines), False

    def scan_loop(self):
        import os, cv2
        debug_dir = os.path.join(os.path.dirname(__file__), "debug_ocr")
        os.makedirs(debug_dir, exist_ok=True)
        scan_count = 0
        
        while self.bot_running:
            try:
                # 1. Lấy tọa độ vùng câu hỏi và vùng đáp án
                qx, qy, qw, qh = self.ui.get_coords_q()
                ox, oy, ow, oh = self.ui.get_coords_opts()
                
                if qw < 10 or qh < 10 or ow < 10 or oh < 10:
                    print(f"[SCAN] Tọa độ quá nhỏ: Q({qx},{qy},{qw},{qh}) O({ox},{oy},{ow},{oh})")
                    break
                
                # Cắt tọa độ nhân với tỷ lệ DPI
                sf = self.scaling_factor
                xq = int(qx * sf)
                yq = int(qy * sf)
                wq = int(qw * sf)
                hq = int(qh * sf)
                
                xopt = int(ox * sf)
                yopt = int(oy * sf)
                wopt = int(ow * sf)
                hopt = int(oh * sf)
                
                if scan_count == 0:
                    print(f"[DEBUG] Scaling Factor: {sf}")
                    print(f"[DEBUG] Q logical: ({qx},{qy},{qw},{qh}) -> physical: ({xq},{yq},{wq},{hq})")
                    print(f"[DEBUG] O logical: ({ox},{oy},{ow},{oh}) -> physical: ({xopt},{yopt},{wopt},{hopt})")
                
                # Phân chia 2x2 cho vùng đáp án:
                half_w = wopt // 2
                half_h = hopt // 2
                
                # Tăng padding lùi vào trong để hoàn toàn tránh viền vàng của overlay
                # (viền có thể dày vài pixel tùy DPI), viền này hay bị Tesseract đọc thành ký tự '|' hoặc 'L'
                pad_w = 10
                pad_h = 10
                
                sub_w = half_w - 2 * pad_w
                sub_h = half_h - 2 * pad_h
                
                if sub_w < 10 or sub_h < 10:
                    print(f"[SCAN] Ô đáp án quá nhỏ sau padding: sub_w={sub_w}, sub_h={sub_h}")
                    time.sleep(0.5)
                    continue
                
                # Tọa độ 4 ô đáp án (A=top-left, B=top-right, C=bottom-left, D=bottom-right)
                xa, ya, wa, ha = xopt + pad_w, yopt + pad_h, sub_w, sub_h
                xb, yb, wb, hb = xopt + half_w + pad_w, yopt + pad_h, sub_w, sub_h
                xc, yc, wc, hc = xopt + pad_w, yopt + half_h + pad_h, sub_w, sub_h
                xd, yd, wd, hd = xopt + half_w + pad_w, yopt + half_h + pad_h, sub_w, sub_h
                
                # Tính bounding box gộp toàn bộ vùng câu hỏi + đáp án
                left = min(xq, xopt)
                top = min(yq, yopt)
                right = max(xq + wq, xopt + wopt)
                bottom = max(yq + hq, yopt + hopt)
                
                entire_w = right - left
                entire_h = bottom - top
                
                if entire_w < 10 or entire_h < 10:
                    time.sleep(0.5)
                    continue
                
                # Chụp 1 ảnh màn hình - app đã thu nhỏ, overlay trong suốt
                # KHÔNG cần ẩn/hiện gì → Không nhấp nháy!
                monitor = {"top": top, "left": left, "width": entire_w, "height": entire_h}
                sct_img = self.sct.grab(monitor)
                img_np = np.array(sct_img)
                
                img_h, img_w_b = img_np.shape[:2]
                
                def get_slice(x1, y1, w1, h1):
                    lx1 = max(0, min(x1 - left, img_w_b))
                    ly1 = max(0, min(y1 - top, img_h))
                    lx2 = max(0, min(x1 - left + w1, img_w_b))
                    ly2 = max(0, min(y1 - top + h1, img_h))
                    return img_np[ly1:ly2, lx1:lx2]
                
                # Cắt lùi vào 5px để tránh viền đỏ của overlay câu hỏi
                q_pad = 5
                q_img = get_slice(xq + q_pad, yq + q_pad, wq - 2*q_pad, hq - 2*q_pad)
                a_img = get_slice(xa, ya, wa, ha)
                b_img = get_slice(xb, yb, wb, hb)
                c_img = get_slice(xc, yc, wc, hc)
                d_img = get_slice(xd, yd, wd, hd)
                
                # Lưu ảnh debug ở lần quét đầu tiên
                if scan_count == 0:
                    print(f"[DEBUG] Captured img: {img_np.shape}, Q: {q_img.shape}, A: {a_img.shape}, B: {b_img.shape}, C: {c_img.shape}, D: {d_img.shape}")
                    for name, img in [("full", img_np), ("question", q_img), ("opt_a", a_img), ("opt_b", b_img), ("opt_c", c_img), ("opt_d", d_img)]:
                        if img.size > 0:
                            cv2.imwrite(os.path.join(debug_dir, f"{name}.png"), img)
                    print(f"[DEBUG] Đã lưu ảnh debug vào thư mục: {debug_dir}")
                
                # OCR câu hỏi (PSM 6 = block of text)
                processed_q = preprocess_for_ocr(q_img, scale=IMAGE_UPSCALING)
                text = pytesseract.image_to_string(processed_q, lang=OCR_LANG, config='--psm 6').strip()
                
                if scan_count == 0:
                    print(f"[DEBUG] OCR Question: '{text[:80]}...'")
                
                # Bỏ qua chuỗi quá ngắn hoặc trùng câu hỏi cũ
                if text and len(text) > 5 and text != self.last_question:
                    self.last_question = text
                    game = self.ui.game_option.get()
                    
                    # Quét chữ 4 đáp án bằng OCR (PSM 7 = single line → tốt hơn cho option ngắn)
                    opts_text = []
                    opt_labels = ['A', 'B', 'C', 'D']
                    for idx, opt_img in enumerate([a_img, b_img, c_img, d_img]):
                        if opt_img.size > 0:
                            proc_opt = preprocess_option_for_ocr(opt_img, scale=IMAGE_UPSCALING)
                            opt_text = pytesseract.image_to_string(proc_opt, lang=OCR_LANG, config='--psm 6').strip()
                            # Làm sạch tiền tố như A., B., C., D. và các ký tự rác ở đầu (đôi khi C bị đọc nhầm thành €)
                            opt_text_cleaned = re.sub(r'^[^a-zA-Z0-9]*[A-Da-d€][\.]?[\s\-\:\)\,\_]*', '', opt_text).strip()
                            # Loại bỏ ký tự rác (chỉ giữ lại dòng có chứa ít nhất 1 chữ/số để tránh xóa mất đáp án 1 chữ số như '2', '3')
                            lines = opt_text_cleaned.split('\n')
                            opt_text_cleaned = ' '.join(l.strip() for l in lines if len(re.sub(r'[^a-zA-Z0-9]', '', l)) > 0)
                            opts_text.append(opt_text_cleaned)
                            if scan_count == 0:
                                print(f"[DEBUG] OCR [{opt_labels[idx]}]: raw='{opt_text[:60]}' -> clean='{opt_text_cleaned[:60]}'")
                        else:
                            opts_text.append("")
                            if scan_count == 0:
                                print(f"[DEBUG] OCR [{opt_labels[idx]}]: EMPTY IMAGE (size=0)")
                            
                    # So khớp và phân tích
                    self.ui.update_qa(text, "Đang tìm câu trả lời & phân tích...")
                    analysis_res, is_db_hit = self.match_and_analyze(game, text, opts_text)
                    self.ui.update_qa(text, analysis_res)
                    
                    if self.ui.switch_sound.get():
                        play_success_beep()
                    
                scan_count += 1
            except Exception as e:
                import traceback
                print(f"[BOT ERROR]: {e}")
                traceback.print_exc()
            time.sleep(0.5)

    def run(self): self.ui.mainloop()

if __name__ == "__main__":
    import sys
    import subprocess
    
    # Xử lý luồng chạy dựa trên tham số dòng lệnh
    if len(sys.argv) > 1:
        if sys.argv[1] == "--admin":
            from src.gui.ui_admin import AdminDashboardApp
            app = AdminDashboardApp()
            app.mainloop()
            sys.exit(0)
        elif sys.argv[1] == "--user":
            app = RoKQuizController()
            app.run()
            sys.exit(0)
            
    # Luồng mặc định: Chạy giao diện đăng nhập
    from src.gui.ui_login import LoginApp
    login_app = LoginApp(None)
    login_app.role_result = None
    login_app.mainloop()
    
    role = getattr(login_app, 'role_result', None)
    try:
        login_app.destroy()
    except:
        pass
        
    # Mở giao diện tương ứng ở một process hoàn toàn mới để tránh lỗi CustomTkinter
    if role == "admin":
        subprocess.Popen([sys.executable, "main.py", "--admin"])
    elif role == "user":
        subprocess.Popen([sys.executable, "main.py", "--user"])