import csv
import os
from src.core.db_manager import RoKDatabase

def sync_and_clean_final():
    csv_path = "quiz_database.csv"
    db_path = "data/rok_quiz.db"
    
    if not os.path.exists(csv_path):
        print("Không tìm thấy file quiz_database.csv!")
        return

    print("Đang quét, làm sạch và loại bỏ trùng lặp trong quiz_database.csv...")
    
    seen_questions = set()
    cleaned_records = []
    duplicate_count = 0
    formatted_count = 0

    # 1. Đọc và dọn dẹp dữ liệu từ file CSV của bạn
    with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None) # Bỏ qua dòng tiêu đề
        for row in reader:
            if len(row) < 3:
                continue
            game = row[0].strip()
            q = row[1].strip()
            a = row[2].strip()
            
            if not q or not a:
                continue
            
            # Loại bỏ trùng lặp (dựa trên Game + Câu hỏi dạng viết thường để so khớp chính xác nhất)
            dup_key = (game.lower(), q.lower())
            if dup_key in seen_questions:
                duplicate_count += 1
                continue
            seen_questions.add(dup_key)
            
            # Chuẩn hóa viết hoa chữ cái đầu tiên cho câu hỏi
            q_before = q
            if q and q[0].islower():
                q = q[0].upper() + q[1:]
                
            # Chuẩn hóa viết hoa cho câu trả lời nếu là chữ cái thường đầu tiên (đáp án thường lịch sự viết hoa đầu từ)
            if a and a[0].islower() and not a.startswith("http") and len(a) > 1:
                # Chỉ viết hoa nếu không phải là ký số hoặc ký hiệu đặc biệt
                if a[0].isalpha():
                    a = a[0].upper() + a[1:]

            if q != q_before:
                formatted_count += 1
                
            cleaned_records.append((game, q, a))

    print(f"-> Quét xong!")
    print(f"-> Đã loại bỏ {duplicate_count} câu bị trùng lặp.")
    print(f"-> Đã định dạng viết hoa cho {formatted_count} câu hỏi.")
    print(f"-> Còn lại {len(cleaned_records)} câu hỏi độc bản, siêu sạch.")

    # 2. Ghi đè lại file quiz_database.csv để đảm bảo file CSV của bạn luôn chuẩn hóa đẹp nhất
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Game', 'Câu hỏi', 'Đáp án'])
        writer.writerows(cleaned_records)
    print("-> Đã cập nhật ghi đè lại file quiz_database.csv.")

    # 3. Đồng bộ hoàn chỉnh vào SQLite database
    print("Đang xóa dữ liệu SQLite cũ để đồng bộ mới tinh...")
    db = RoKDatabase(db_path)
    db.cursor.execute("DELETE FROM questions")
    db.conn.commit()

    added_count = 0
    for game, q, a in cleaned_records:
        if db.add_question(game, q, a):
            added_count += 1

    print(f"-> Đồng bộ SQLite thành công!")
    print(f"-> Đã nạp {added_count} câu hỏi độc nhất, siêu sạch vào SQLite.")
    
if __name__ == "__main__":
    sync_and_clean_final()
