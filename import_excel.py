
import openpyxl
import os
import sys

# Thêm thư mục hiện tại vào path để import được src
sys.path.append(os.getcwd())

from src.core.db_manager import RoKDatabase

def import_from_excel(file_path):
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file {file_path}")
        return

    print(f"--- Đang đọc file: {file_path} ---")
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        # Thử đọc Sheet2 như trong ảnh, nếu không có thì đọc sheet đầu tiên
        sheet = wb['Sheet2'] if 'Sheet2' in wb.sheetnames else wb.active
        print(f"Đang xử lý sheet: {sheet.title}")

        db = RoKDatabase()
        
        count = 0
        duplicate = 0
        
        # Duyệt từ dòng 1 (hoặc dòng bạn muốn, ví dụ trong ảnh là dòng 1236)
        # Ở đây mình duyệt toàn bộ có dữ liệu
        for row in sheet.iter_rows(min_row=1, values_only=True):
            if not row or len(row) < 2:
                continue
                
            question = str(row[0]).strip() if row[0] else ""
            answer = str(row[1]).strip() if row[1] else ""
            
            # Bỏ qua nếu dữ liệu trống hoặc tiêu đề
            if not question or not answer or question.lower() == "câu hỏi":
                continue
            
            # Giả định mặc định là Rise of Kingdoms, bạn có thể chỉnh lại nếu cần
            if db.add_question("Rise of Kingdoms", question, answer):
                count += 1
            else:
                duplicate += 1
                
        print(f"Hoàn tất! Thêm mới: {count} câu. Trùng lặp: {duplicate} câu.")
        
    except Exception as e:
        print(f"Lỗi khi xử lý: {e}")

if __name__ == "__main__":
    file_name = "ROK Question.xlsx"
    import_from_excel(file_name)
