
import os
import sys
import re

# Thêm thư mục hiện tại vào path để import được src
sys.path.append(os.getcwd())

from src.core.db_manager import RoKDatabase

def parse_ali213(content):
    questions = []
    # Q: ... A: ... or Q：... A：...
    q_pattern = re.compile(r'Q[：:](.*?)\nA[：:](.*?)(?:\n|$)', re.DOTALL)
    matches = q_pattern.findall(content)
    for q, a in matches:
        questions.append((q.strip(), a.strip()))
    return questions

def parse_cod_guide(content):
    questions = []
    # Pattern for cod.guide: Question text followed by answer text on same or next line
    # Based on content.md, it looks like: "Question text? Answer text"
    lines = content.split('\n')
    for line in lines:
        if '?' in line:
            # Simple split by last '?'
            parts = line.rsplit('?', 1)
            if len(parts) == 2:
                q = parts[0].strip() + "?"
                a = parts[1].strip()
                if 10 < len(q) < 500 and 0 < len(a) < 200:
                    questions.append((q, a))
    return questions

def import_scraped():
    db = RoKDatabase()
    
    # Lấy đường dẫn từ cấu hình (đã được nạp từ .env)
    from src.core.config import ALI_PATH, COD_PATH
    ali_path = ALI_PATH
    cod_path = COD_PATH
    
    total_added = 0
    
    if os.path.exists(ali_path):
        with open(ali_path, 'r', encoding='utf-8') as f:
            content = f.read()
            qs = parse_ali213(content)
            print(f"Tìm thấy {len(qs)} câu từ Ali213 (tiếng Trung).")
            for q, a in qs:
                # Import bản gốc tiếng Trung
                if db.add_question("Call of Dragons", q, a):
                    total_added += 1
    
    if os.path.exists(cod_path):
        with open(cod_path, 'r', encoding='utf-8') as f:
            content = f.read()
            qs = parse_cod_guide(content)
            print(f"Tìm thấy {len(qs)} câu từ cod.guide (tiếng Anh).")
            for q, a in qs:
                if db.add_question("Call of Dragons", q, a):
                    total_added += 1
                    
    print(f"Hoàn thành nạp dữ liệu cào được! Tổng cộng thêm mới: {total_added} câu.")

if __name__ == "__main__":
    import_scraped()
