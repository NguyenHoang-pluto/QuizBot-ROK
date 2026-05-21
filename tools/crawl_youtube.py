import os
import sys
import re
import requests

# Thêm thư mục hiện tại vào path để import được src
sys.path.append(os.getcwd())

from src.core.db_manager import RoKDatabase
# Nếu trong file config có cấu hình thì lấy, không thì dùng os.getenv trực tiếp
try:
    from src.core.config import YOUTUBE_API_KEY
except ImportError:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

def extract_qa(text):
    questions = []
    # Pattern 1: Q: ... A: ...
    pattern = re.compile(r'(?:Q:|Question:)\s*(.*?)(?:\n|A:|Answer:)\s*(?:A:|Answer:)?\s*(.*?)(?:\n\n|\Z)', re.IGNORECASE | re.DOTALL)
    matches = pattern.findall(text)
    
    for q, a in matches:
        q = q.strip()
        a = a.strip()
        if q and a and len(q) < 500 and len(a) < 200:
            if not q.endswith('?'):
                q += '?'
            questions.append((q, a))
            
    # Pattern 2: (Câu kết thúc bằng ?) (Câu trả lời ở ngay dưới)
    if not questions:
        lines = text.split('\n')
        for i in range(len(lines) - 1):
            line = lines[i].strip()
            next_line = lines[i+1].strip()
            if line.endswith('?') and len(line) > 10 and next_line and len(next_line) < 100:
                if not next_line.endswith('?'):
                    questions.append((line, next_line))
                    
    return questions

def crawl_youtube():
    print("Đang cào dữ liệu từ YouTube...")
    
    # Lấy API key từ biến môi trường nếu không có trong config
    api_key = YOUTUBE_API_KEY or os.getenv('YOUTUBE_API_KEY', '')
    
    if not api_key or api_key == 'your_youtube_api_key_here':
        print("LỖI: Bạn chưa cấu hình YOUTUBE_API_KEY trong file .env!")
        print("Vui lòng truy cập Google Cloud Console, tạo một API Key cho YouTube Data API v3 và thêm vào file .env.")
        return

    # Tìm kiếm các video mới nhất
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        'part': 'snippet',
        'q': 'Call of Dragons Vale Society Quiz Answers',
        'type': 'video',
        'maxResults': 50, # Tăng lên 50 video để tìm được nhiều hơn
        'order': 'relevance', # Ưu tiên mức độ liên quan
        'key': api_key
    }
    
    questions_answers = []
    
    try:
        r = requests.get(search_url, params=search_params)
        if r.status_code == 200:
            data = r.json()
            items = data.get('items', [])
            print(f"Đã tìm thấy {len(items)} video liên quan.")
            
            for item in items:
                video_id = item['id']['videoId']
                
                # Gọi thêm API videos
                video_url = "https://www.googleapis.com/youtube/v3/videos"
                video_params = {
                    'part': 'snippet',
                    'id': video_id,
                    'key': api_key
                }
                
                v_req = requests.get(video_url, params=video_params)
                if v_req.status_code == 200:
                    v_data = v_req.json()
                    if v_data.get('items'):
                        full_desc = v_data['items'][0]['snippet']['description']
                        qs = extract_qa(full_desc)
                        questions_answers.extend(qs)
        else:
            print(f"Lỗi từ YouTube API: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Lỗi kết nối YouTube API: {e}")
        
    unique_qa = list(set(questions_answers))
    print(f"Đã trích xuất được {len(unique_qa)} câu hỏi độc nhất từ YouTube.")
    
    db = RoKDatabase()
    total_added = 0
    for q, a in unique_qa:
        if db.add_question("Call of Dragons", q, a):
            total_added += 1
            
    # Tự động xuất (đồng bộ) ra file CSV
    db.export_to_csv("data/quiz_database.csv")
    print(f"Hoàn thành! Đã thêm mới {total_added} câu hỏi vào database và đồng bộ thẳng vào file quiz_database.csv.")

if __name__ == "__main__":
    crawl_youtube()
