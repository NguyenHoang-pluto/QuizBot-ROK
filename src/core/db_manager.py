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
        text = self.remove_accents(text)
        text = "".join(e for e in text if e.isalnum()).lower()
        return text

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

    def find_answer(self, game, question_text):
        if not question_text: return None
        target_clean = self.normalize_text(question_text)
        
        q_hash = hashlib.md5(target_clean.encode()).hexdigest()
        self.cursor.execute("SELECT answer_text FROM questions WHERE game = ? AND hash = ?", (game, q_hash))
        result = self.cursor.fetchone()
        if result: return result[0]
        
        self.cursor.execute("SELECT question_text, answer_text FROM questions WHERE game = ?", (game,))
        all_questions = self.cursor.fetchall()
        
        best_match = None
        highest_ratio = 0.0
        for q_txt, a_txt in all_questions:
            q_clean = self.normalize_text(q_txt)
            ratio = SequenceMatcher(None, target_clean, q_clean).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = a_txt
        
        if highest_ratio > 0.75: return best_match
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
