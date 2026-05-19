import csv
import re
import os
from src.core.db_manager import RoKDatabase

def clean_leftovers_script():
    csv_path = "quiz_database.csv"
    if not os.path.exists(csv_path):
        print("Không tìm thấy file quiz_database.csv!")
        return

    print("Đang quét và làm sạch các tàn dư trong quiz_database.csv...")
    cleaned_records = []
    removed_count = 0
    fixed_count = 0

    with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            game = row[0].strip()
            q = row[1].strip()
            a = row[2].strip()

            # 1. Loại bỏ các dòng rác thảo luận hoặc câu hỏi rác chỉ chứa chữ "Q", "Q.", "A", "MỘT"
            q_lower = q.lower().strip()
            a_lower = a.lower().strip()
            
            # Loại bỏ nếu câu hỏi chứa thông tin bình luận thảo luận rác (như Moosa...)
            if "moosa" in q_lower or "nairdat" in q_lower or "jellow" in q_lower or "boomitsrichyt" in q_lower:
                removed_count += 1
                continue
            
            # Loại bỏ nếu câu hỏi hoặc đáp án quá ngắn và vô nghĩa
            if q_lower in ['q', 'q.', 'a', 'a.', 'một'] or a_lower in ['q', 'q.', 'a', 'a.', 'một']:
                removed_count += 1
                continue

            # 2. Xóa các tiền tố thời gian tàn dư ở đầu câu hỏi
            q_before = q
            
            # Xóa cụm "đăng ngày... lúc, 15 giờ sáng " ở đầu câu
            q = re.sub(
                r'^(đăng\s+ngày|được\s+xuất\s+bản\s+ngày)\s+\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}\s+lúc\s*,\s*\d{1,2}\s+giờ\s*(sáng|chiều|tối)?\s*',
                '', q, flags=re.IGNORECASE
            ).strip()

            # Xóa các cụm "giờ sáng ", "giờ chiều ", "giờ tối " ở đầu câu
            q = re.sub(
                r'^(giờ\s+(sáng|chiều|tối|tối)\b|h\b|g\b|am\b|pm\b|,\s*)+',
                '', q, flags=re.IGNORECASE
            ).strip()
            
            # Làm sạch ký tự phân cách ở đầu/cuối sau khi xóa tiền tố
            q = q.strip().lstrip(',').lstrip('–').lstrip('-').lstrip(':').strip()
            q = q.strip().rstrip('–').rstrip('-').rstrip(':').strip()
            a = a.strip().rstrip('–').rstrip('-').rstrip(':').strip()

            # Viết hoa lại chữ cái đầu tiên của câu hỏi nếu bị biến thành chữ thường sau khi cắt
            if q and q[0].islower():
                q = q[0].upper() + q[1:]

            if q != q_before:
                fixed_count += 1

            # Lọc kỹ lại sau khi đã làm sạch
            if len(q) > 15 and len(a) > 0:
                cleaned_records.append((game, q, a))
            else:
                removed_count += 1

    print(f"Tổng số câu đã dọn sạch tàn dư thành công: {fixed_count} câu.")
    print(f"Tổng số câu rác/thảo luận đã loại bỏ hoàn toàn: {removed_count} câu.")
    print(f"Còn lại {len(cleaned_records)} câu hỏi cực kỳ chất lượng.")

    # 3. Ghi đè lại file CSV
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Game', 'Câu hỏi', 'Đáp án'])
        writer.writerows(cleaned_records)
    print("Đã ghi đè cập nhật lại file quiz_database.csv.")

    # 4. Đồng bộ ngược lại SQLite database để lưu trữ vĩnh viễn
    print("Đang đồng bộ ngược lại vào SQLite...")
    db = RoKDatabase("data/rok_quiz.db")
    db.cursor.execute("DELETE FROM questions")
    db.conn.commit()

    added_count = 0
    for game, q, a in cleaned_records:
        if db.add_question(game, q, a):
            added_count += 1

    print(f"Đã cập nhật đồng bộ hoàn tất SQLite! Tổng số câu trong kho: {added_count}")

if __name__ == "__main__":
    clean_leftovers_script()
