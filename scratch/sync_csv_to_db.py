import sqlite3
import csv
import os
import hashlib
from src.core.db_manager import RoKDatabase

def sync_csv_to_sqlite():
    csv_path = "quiz_database.csv"
    db_path = "data/rok_quiz.db"
    
    if not os.path.exists(csv_path):
        print("Không tìm thấy file quiz_database.csv!")
        return

    print("Đang đọc file quiz_database.csv...")
    records = []
    
    # Đọc file CSV đã được bạn dọn dẹp bằng tay
    with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None) # Bỏ qua dòng tiêu đề
        for row in reader:
            if len(row) >= 3:
                game = row[0].strip()
                q = row[1].strip()
                a = row[2].strip()
                if q and a:
                    records.append((game, q, a))

    print(f"Đọc thành công {len(records)} câu hỏi từ file CSV của bạn.")

    # Kết nối tới database
    db = RoKDatabase(db_path)
    
    # Xóa sạch bảng câu hỏi cũ trong SQLite
    print("Đang làm sạch cơ sở dữ liệu SQLite cũ...")
    db.cursor.execute("DELETE FROM questions")
    db.conn.commit()

    # Nạp toàn bộ dữ liệu từ CSV của bạn vào SQLite
    added_count = 0
    for game, q, a in records:
        if db.add_question(game, q, a):
            added_count += 1

    print(f"Đồng bộ thành công! Đã nạp {added_count} câu hỏi siêu sạch vào SQLite.")
    
if __name__ == "__main__":
    sync_csv_to_sqlite()
