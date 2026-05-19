import sqlite3
import os
import re
from src.core.db_manager import RoKDatabase
from src.logic.crawler import clean_comment_headers

def advanced_database_recovery():
    db_path = "data/rok_quiz.db"
    if not os.path.exists(db_path):
        print("Không tìm thấy tệp cơ sở dữ liệu!")
        return

    print("Đang kết nối tới cơ sở dữ liệu SQLite...")
    db = RoKDatabase(db_path)
    
    # 1. Đọc toàn bộ các câu hỏi hiện có
    db.cursor.execute("SELECT game, question_text, answer_text FROM questions")
    rows = db.cursor.fetchall()
    print(f"Tổng số bản ghi trong DB hiện tại: {len(rows)}")

    recovered_items = []
    skipped_count = 0
    direct_clean_count = 0
    merge_recover_count = 0

    # 2. Xử lý từng bản ghi
    for game, q, a in rows:
        # Nhận diện dòng bị cắt lỗi do dấu ":" trong giờ phút bình luận
        # Dấu hiệu: q kết thúc bằng số giờ, a bắt đầu bằng phút và có dấu "?" trong a
        is_corrupt_split = False
        
        # Kiểm tra nếu câu hỏi kết thúc bằng số giờ (ví dụ: "at 3" hoặc "lúc 12")
        q_ends_with_hour = re.search(r'(at|@|lúc)\s+\d{1,2}$', q, re.IGNORECASE) is not None
        # Kiểm tra nếu đáp án bắt đầu bằng phút (ví dụ: "24 pm" hoặc "19 am" hoặc "15 giờ")
        a_starts_with_minutes = re.match(r'^\d{2}\s*(am|pm|AM|PM|giờ|g|h|phút)\b', a, re.IGNORECASE) is not None
        
        if q_ends_with_hour and a_starts_with_minutes and "?" in a:
            is_corrupt_split = True

        if is_corrupt_split:
            # TIẾN HÀNH GHÉP NỐI KHÔI PHỤC
            merged_text = q + ":" + a
            cleaned = clean_comment_headers(merged_text)
            
            # Tách lại chuẩn xác theo dấu "?"
            if "?" in cleaned:
                parts = cleaned.split("?", 1)
                q_new = parts[0].strip() + "?"
                a_new = parts[1].strip()
                
                # Làm sạch các ký tự phân cách thừa
                q_new = q_new.strip().rstrip('–').rstrip('-').rstrip(':').strip()
                a_new = a_new.strip().rstrip('–').rstrip('-').rstrip(':').strip()
                
                if len(q_new) > 15 and len(a_new) > 0:
                    recovered_items.append((game, q_new, a_new))
                    merge_recover_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1
        else:
            # Dòng bình thường: Chỉ cần chạy bộ lọc dọn dẹp trực tiếp
            q_cleaned = clean_comment_headers(q)
            a_cleaned = clean_comment_headers(a)
            
            q_cleaned = q_cleaned.strip().rstrip('–').rstrip('-').rstrip(':').strip()
            a_cleaned = a_cleaned.strip().rstrip('–').rstrip('-').rstrip(':').strip()
            
            if len(q_cleaned) > 15 and len(a_cleaned) > 0:
                recovered_items.append((game, q_cleaned, a_cleaned))
                direct_clean_count += 1
            else:
                skipped_count += 1

    print(f"Khôi phục ghép nối thành công: {merge_recover_count} câu bị cắt sai!")
    print(f"Làm sạch trực tiếp thành công: {direct_clean_count} câu chuẩn!")
    print(f"Đã lọc bỏ rác dư thừa: {skipped_count} dòng.")

    # 3. Xóa và nạp lại DB siêu sạch
    db.cursor.execute("DELETE FROM questions")
    db.conn.commit()

    added_count = 0
    for game, q, a in recovered_items:
        if db.add_question(game, q, a):
            added_count += 1

    print(f"Đã lưu thành công {added_count} câu hỏi cực sạch vào SQLite!")
    
    # 4. Xuất đồng bộ đè lên file CSV
    csv_name = db.export_to_csv("quiz_database.csv")
    print(f"Đã cập nhật đồng bộ hoàn tất file CSV: {csv_name}")

if __name__ == "__main__":
    advanced_database_recovery()
