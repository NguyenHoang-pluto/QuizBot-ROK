import os
import sys

# Thêm thư mục hiện tại vào path để import được src
sys.path.append(os.getcwd())

from src.core.db_manager import RoKDatabase

def bulk_import():
    db = RoKDatabase()
    
    # Dữ liệu thực tế cho Rise of Kingdoms
    rok_questions = [
        ("Ai là người sáng lập ra Rome?", "Romulus"),
        ("Đơn vị quân đặc biệt của Pháp là gì?", "Hiệp sĩ ném lao"),
        ("Ai được gọi là 'Kẻ Chinh Phục'?", "William I"),
        ("Tài nguyên nào không thể thu hoạch ở bản đồ thế giới?", "Gỗ"),
        ("Tôn Tử là tướng của quốc gia nào?", "Trung Quốc"),
        ("Tướng nào có biệt danh là 'Hoa Mộc Lan'?", "Mulan"),
        ("Quốc gia nào có đơn vị đặc biệt là Teutonic Knight?", "Đức")
    ]
    
    # Dữ liệu cho Call of Dragons
    cod_questions = [
        ("Tướng nào mạnh nhất về phép thuật?", "Waldyr"),
        ("Đơn vị bay của tộc Tiên là gì?", "Cung thủ đại bàng"),
        ("Lực lượng nào chuyên đi thu thập tài nguyên?", "Công binh")
    ]
    
    print("--- Đang nạp dữ liệu ---")
    for q, a in rok_questions:
        db.add_question("Rise of Kingdoms", q, a)
        
    for q, a in cod_questions:
        db.add_question("Call of Dragons", q, a)
        
    print("Xong! Đã nạp thành công. Bây giờ bạn hãy mở Tool lên test thử nhé.")

if __name__ == "__main__":
    bulk_import()
