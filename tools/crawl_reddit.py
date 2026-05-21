import os
import sys
import re
import requests
import cv2
import numpy as np
import pytesseract
import tempfile
import shutil

# Thêm thư mục hiện tại vào path để import được src
sys.path.append(os.getcwd())

from src.core.db_manager import RoKDatabase
from src.core.config import TESSERACT_PATH, OCR_LANG
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def validate_and_extract_qa(text):
    """
    Kiểm tra và trích xuất dữ liệu, chỉ lấy nếu đúng định dạng.
    Trả về danh sách các tuple (câu hỏi, câu trả lời) hợp lệ.
    """
    questions = []
    
    # Cách 1: Q: ... A: ...
    pattern = re.compile(r'(?:Q:|Question:)\s*(.*?)(?:\n|A:|Answer:)\s*(?:A:|Answer:)?\s*(.*?)(?:\n\n|\Z)', re.IGNORECASE | re.DOTALL)
    matches = pattern.findall(text)
    
    for q, a in matches:
        q = q.strip()
        a = a.strip()
        # Validation: Câu hỏi dài 10-500 ký tự, Câu trả lời dài 1-200 ký tự
        if q and a and 10 < len(q) < 500 and 0 < len(a) < 200:
            if not q.endswith('?'):
                q += '?'
            questions.append((q, a))
            
    # Cách 2: Dòng kết thúc bằng '?' và dòng tiếp theo là đáp án ngắn
    if not questions:
        lines = text.split('\n')
        for i in range(len(lines) - 1):
            line = lines[i].strip()
            next_line = lines[i+1].strip()
            
            # Validation: Dòng hiện tại là câu hỏi hợp lý
            if line.endswith('?') and 10 < len(line) < 300:
                # Validation: Dòng dưới không rỗng, không phải câu hỏi, và có độ dài hợp lý cho một đáp án
                if next_line and not next_line.endswith('?') and len(next_line) < 150:
                    questions.append((line, next_line))
                    
    return questions

def ocr_image_to_text(image_path):
    """Sử dụng OCR để đọc chữ từ ảnh, áp dụng xử lý ảnh giống test_ocr2.py"""
    img = cv2.imread(image_path)
    if img is None:
        return ""
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # Dùng ngưỡng tốt nhất từ bài test của bạn (thường là THRESH_BINARY_INV -10)
    proc = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, -10)
    
    # Cấu hình psm 6 giúp đọc các khối văn bản đồng nhất (rất tốt cho câu hỏi đáp án)
    text = pytesseract.image_to_string(proc, lang=OCR_LANG, config='--psm 6').strip()
    return text

def crawl_reddit():
    print("Đang cào dữ liệu từ Reddit (r/callofdragons)...")
    url = "https://www.reddit.com/r/callofdragons/search.json?q=quiz OR Vale Society&restrict_sr=on&limit=100"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    
    questions_answers = []
    
    # Tạo thư mục tạm để lưu ảnh tải về
    temp_dir = tempfile.mkdtemp()
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            posts = data.get('data', {}).get('children', [])
            print(f"Đã tìm thấy {len(posts)} bài post liên quan.")
            
            for post in posts:
                post_data = post.get('data', {})
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                post_url = post_data.get('url', '')
                
                print(f"\n--- Xử lý bài: {title} ---")
                
                extracted_from_text = []
                
                # 1. Trích xuất từ Text thông thường (nếu có)
                if selftext:
                    extracted_from_text = validate_and_extract_qa(selftext)
                    if extracted_from_text:
                        print(f" -> Quét được {len(extracted_from_text)} cặp hỏi-đáp từ phần nội dung văn bản.")
                        questions_answers.extend(extracted_from_text)
                
                # 2. Trích xuất từ Hình Ảnh qua OCR (nếu bài post đính kèm ảnh)
                # Chỉ lấy những bài post chưa quét được text nào và có chứa ảnh
                if not extracted_from_text and post_url.endswith(('.png', '.jpg', '.jpeg')) or 'i.redd.it' in post_url:
                    print(f" -> Phát hiện bài post chứa ảnh. Đang tải ảnh về để chạy OCR...")
                    try:
                        img_response = requests.get(post_url, headers=headers, stream=True)
                        if img_response.status_code == 200:
                            img_path = os.path.join(temp_dir, 'temp_reddit_img.png')
                            with open(img_path, 'wb') as f:
                                img_response.raw.decode_content = True
                                shutil.copyfileobj(img_response.raw, f)
                            
                            # Chạy OCR
                            ocr_text = ocr_image_to_text(img_path)
                            
                            # Dùng hàm validate để kiểm tra định dạng nội dung OCR
                            extracted_from_ocr = validate_and_extract_qa(ocr_text)
                            if extracted_from_ocr:
                                print(f" -> THÀNH CÔNG! Đã dùng OCR bóc tách được {len(extracted_from_ocr)} cặp hỏi-đáp từ ảnh.")
                                questions_answers.extend(extracted_from_ocr)
                            else:
                                print(f" -> OCR chạy xong nhưng dữ liệu text không thỏa mãn định dạng câu hỏi.")
                    except Exception as img_e:
                        print(f" -> Lỗi khi xử lý ảnh: {img_e}")

        else:
            print(f"Lỗi khi truy cập Reddit: {r.status_code}")
    except Exception as e:
        print(f"Lỗi kết nối Reddit: {e}")
    finally:
        # Xóa thư mục ảnh tạm
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    unique_qa = list(set(questions_answers))
    print(f"\n=============================")
    print(f"Đã trích xuất và VALIDATE được {len(unique_qa)} câu hỏi độc nhất từ Reddit.")
    
    db = RoKDatabase()
    total_added = 0
    for q, a in unique_qa:
        # Bước validate cuối cùng ở mức Database (nếu add_question cho phép)
        if db.add_question("Call of Dragons", q, a):
            total_added += 1
            
    # Tự động đồng bộ sang file CSV
    db.export_to_csv("data/quiz_database.csv")
    print(f"Hoàn thành! Đã lưu mới {total_added} câu hỏi đạt chuẩn vào cơ sở dữ liệu và đồng bộ vào file CSV.")

if __name__ == "__main__":
    crawl_reddit()
