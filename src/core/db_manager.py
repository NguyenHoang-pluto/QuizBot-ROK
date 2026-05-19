import sqlite3
import hashlib
import os
import unicodedata
import csv
from datetime import datetime
from difflib import SequenceMatcher

class RoKDatabase:
    def __init__(self, db_path="data/rok_quiz.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT,
                hash TEXT,
                question_text TEXT,
                answer_text TEXT,
                UNIQUE(game, hash)
            )
        ''')
        try:
            self.cursor.execute("SELECT game FROM questions LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE questions ADD COLUMN game TEXT DEFAULT 'Rise of Kingdoms'")
        self.conn.commit()

    def remove_accents(self, input_str):
        if not input_str: return ""
        s = unicodedata.normalize('NFD', input_str)
        s = "".join([c for c in s if unicodedata.category(c) != 'Mn'])
        s = s.replace('đ', 'd').replace('Đ', 'D')
        return s

    def normalize_text(self, text):
        if not text: return ""
        text = self.remove_accents(text)
        # Giữ lại khoảng trắng, chữ và số, thay thế ký tự đặc biệt bằng khoảng trắng
        text = "".join(e if e.isalnum() or e.isspace() else " " for e in text)
        # Thu gọn khoảng trắng và viết thường
        return " ".join(text.split()).lower()

    def add_question(self, game, question, answer):
        """Trả về True nếu thêm mới thành công, False nếu đã tồn tại"""
        clean_q = self.normalize_text(question)
        q_hash = hashlib.md5(clean_q.encode()).hexdigest()
        try:
            self.cursor.execute(
                "INSERT INTO questions (game, hash, question_text, answer_text) VALUES (?, ?, ?, ?)",
                (game, q_hash, question, answer)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except: 
            return False

    def save_or_update_question(self, game, question, answer):
        """Thêm mới hoặc cập nhật đáp án nếu câu hỏi đã tồn tại"""
        if not question or not answer: return False
        clean_q = self.normalize_text(question)
        q_hash = hashlib.md5(clean_q.encode()).hexdigest()
        try:
            self.cursor.execute(
                "INSERT INTO questions (game, hash, question_text, answer_text) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(game, hash) DO UPDATE SET answer_text = ?, question_text = ?",
                (game, q_hash, question, answer, answer, question)
            )
            self.conn.commit()
            return True
        except Exception as e:
            try:
                self.cursor.execute(
                    "INSERT OR REPLACE INTO questions (game, hash, question_text, answer_text) VALUES (?, ?, ?, ?)",
                    (game, q_hash, question, answer)
                )
                self.conn.commit()
                return True
            except Exception as ex:
                print(f"[DB ERROR]: {ex}")
                return False

    def calculate_match_score(self, target_clean, q_clean):
        """Tính điểm tương đồng kết hợp giữa độ tương đồng ký tự (SequenceMatcher),
        độ trùng khớp từ khóa (Jaccard) và tỷ lệ phủ từ khóa (Overlap)"""
        # 1. Điểm tương đồng ký tự (SequenceMatcher)
        ratio = SequenceMatcher(None, target_clean, q_clean).ratio()
        
        w_target = set(target_clean.split())
        w_db = set(q_clean.split())
        if not w_target or not w_db:
            return ratio
            
        # 2. Điểm tương đồng từ khóa Jaccard (Số từ trùng khớp / Tổng số từ duy nhất)
        intersect = w_target.intersection(w_db)
        union = w_target.union(w_db)
        jaccard = len(intersect) / len(union) if union else 0.0
        
        # 3. Điểm tỷ lệ phủ từ khóa Overlap (Số từ trùng khớp / Độ dài câu ngắn hơn)
        # Chỉ áp dụng nếu cả hai câu đều dài từ 3 từ trở lên để tránh so khớp nhầm câu siêu ngắn
        overlap = 0.0
        if len(w_target) >= 3 and len(w_db) >= 3:
            overlap = len(intersect) / min(len(w_target), len(w_db))
            
        # Trả về điểm số cao nhất. Trọng số overlap nhân 0.9 để Sequence/Jaccard vẫn được ưu tiên hơn
        return max(ratio, jaccard, overlap * 0.9)

    def find_answer(self, game, question_text):
        if not question_text: return None
        target_clean = self.normalize_text(question_text)
        
        # 1. Tìm chính xác trong game đã chọn
        q_hash = hashlib.md5(target_clean.encode()).hexdigest()
        self.cursor.execute("SELECT answer_text FROM questions WHERE game = ? AND hash = ?", (game, q_hash))
        result = self.cursor.fetchone()
        if result: return result[0]
        
        # 2. Tìm gần đúng (Fuzzy/Semantic) trong game đã chọn
        self.cursor.execute("SELECT question_text, answer_text FROM questions WHERE game = ?", (game,))
        all_questions = self.cursor.fetchall()
        
        best_match = None
        best_q_text = None
        highest_score = 0.0
        for q_txt, a_txt in all_questions:
            q_clean = self.normalize_text(q_txt)
            score = self.calculate_match_score(target_clean, q_clean)
            if score > highest_score:
                highest_score = score
                best_match = a_txt
                best_q_text = q_txt
        
        if highest_score > 0.75: 
            return best_match
        elif highest_score > 0.45:
            pct = int(highest_score * 100)
            return f"[Gợi ý {pct}%]: {best_match}\n(Cho câu: {best_q_text})"
        
        # 3. Hỗ trợ dự phòng (Fallback): Tìm ở game còn lại nếu chọn nhầm game
        other_game = "Call of Dragons" if game == "Rise of Kingdoms" else "Rise of Kingdoms"
        
        # Thử tìm chính xác ở game còn lại
        self.cursor.execute("SELECT answer_text FROM questions WHERE game = ? AND hash = ?", (other_game, q_hash))
        result_other = self.cursor.fetchone()
        if result_other: 
            return f"{result_other[0]} (Gợi ý từ {other_game})"
            
        # Thử tìm gần đúng ở game còn lại
        self.cursor.execute("SELECT question_text, answer_text FROM questions WHERE game = ?", (other_game,))
        all_questions_other = self.cursor.fetchall()
        
        best_match_other = None
        best_q_text_other = None
        highest_score_other = 0.0
        for q_txt, a_txt in all_questions_other:
            q_clean = self.normalize_text(q_txt)
            score = self.calculate_match_score(target_clean, q_clean)
            if score > highest_score_other:
                highest_score_other = score
                best_match_other = a_txt
                best_q_text_other = q_txt
                
        if highest_score_other > 0.75: 
            return f"{best_match_other} (Gợi ý từ {other_game})"
        elif highest_score_other > 0.45:
            pct = int(highest_score_other * 100)
            return f"[Gợi ý {pct}% từ {other_game}]: {best_match_other}\n(Cho câu: {best_q_text_other})"
            
        return None

    def export_to_csv(self, custom_name=""):
        """Xuất database ra file CSV với tên tự chọn hoặc tự động"""
        try:
            # Tạo tên file
            if not custom_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"quiz_export_{timestamp}.csv"
            else:
                filename = custom_name if custom_name.endswith(".csv") else f"{custom_name}.csv"

            self.cursor.execute("SELECT game, question_text, answer_text FROM questions")
            rows = self.cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Game', 'Câu hỏi', 'Đáp án'])
                writer.writerows(rows)
            return filename
        except:
            return None

    def get_stats(self):
        self.cursor.execute("SELECT game, count(*) FROM questions GROUP BY game")
        return self.cursor.fetchall()
