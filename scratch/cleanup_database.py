import sqlite3
import os
import re
import csv
import hashlib
from src.core.db_manager import RoKDatabase
from src.logic.crawler import clean_comment_headers

def clean_database_records():
    db_path = "data/rok_quiz.db"
    if not os.path.exists(db_path):
        print("Không tìm thấy tệp cơ sở dữ liệu!")
        return

    print("Đang kết nối tới cơ sở dữ liệu...")
    db = RoKDatabase(db_path)
    
    # 1. Đọc toàn bộ các câu hỏi hiện có
    db.cursor.execute("SELECT game, question_text, answer_text FROM questions")
    rows = db.cursor.fetchall()
    print(f"Tổng số bản ghi ban đầu: {len(rows)}")

    cleaned_items = []
    skipped_count = 0

    # 2. Làm sạch từng câu hỏi và đáp án
    for game, q, a in rows:
        q_cleaned = clean_comment_headers(q)
        a_cleaned = clean_comment_headers(a)

        # Lọc sạch các ký tự phân cách thừa ở hai đầu câu
        q_cleaned = q_cleaned.strip().rstrip('–').rstrip('-').rstrip(':').strip()
        a_cleaned = a_cleaned.strip().rstrip('–').rstrip('-').rstrip(':').strip()

        # Kiểm tra xem câu hỏi có chứa định dạng rác hoặc quá ngắn sau khi dọn sạch không
        # Ví dụ: "Moosa September 6, 2022 at 5,14 pm Q" sau khi xóa sẽ chỉ còn "Q"
        if len(q_cleaned) <= 15 or len(a_cleaned) == 0:
            skipped_count += 1
            continue
        
        cleaned_items.append((game, q_cleaned, a_cleaned))

    print(f"Số bản ghi đã dọn sạch: {len(cleaned_items)}")
    print(f"Số bản ghi rác/trùng lặp đã loại bỏ hoàn toàn: {skipped_count}")

    # 3. Xóa bảng questions cũ
    db.cursor.execute("DELETE FROM questions")
    db.conn.commit()

    # 4. Nạp lại các bản ghi đã được làm sạch và loại bỏ trùng lặp bằng add_question
    added_count = 0
    for game, q, a in cleaned_items:
        if db.add_question(game, q, a):
            added_count += 1

    print(f"Đã lưu lại thành công {added_count} câu hỏi siêu sạch vào cơ sở dữ liệu SQLite!")
    
    # 5. Xuất đồng bộ ra CSV
    csv_name = db.export_to_csv("quiz_database.csv")
    print(f"Đã xuất đồng bộ dữ liệu siêu sạch ra file: {csv_name}")

if __name__ == "__main__":
    clean_database_records()
