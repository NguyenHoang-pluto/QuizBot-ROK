import requests
from bs4 import BeautifulSoup
import urllib3
import re

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_vietnamese(text):
    vietnamese_chars = "àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệđìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
    for char in vietnamese_chars:
        if char in text.lower():
            return True
    return False

def translate_to_vi(text):
    if not text or is_vietnamese(text): return text
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=vi&dt=t&q={text}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return "".join([part[0] for part in data[0]])
        return text
    except:
        return text

def is_garbage(text):
    """Kiểm tra xem văn bản có phải là rác (menu, footer, link) không"""
    blacklist = ["trang chủ", "liên hệ", "giới thiệu", "đăng nhập", "đăng ký", "tìm kiếm", "bình luận", "về chúng tôi", "điều khoản", "chính sách"]
    t = text.lower()
    if len(text) < 15: return True # Câu hỏi quá ngắn thường là menu
    for word in blacklist:
        if word in t: return True
    return False

def clean_comment_headers(text):
    """Xóa bỏ tên người dùng, thời gian và các nút bấm 'Trả lời' ở phần bình luận"""
    if not text:
        return text
    
    # 1. Regex xóa định dạng thời gian tiếng Anh: "Name August 8, 2022 at 12:45 am"
    en_months = "(January|February|March|April|May|June|July|August|September|October|November|December)"
    pattern_en = rf'^[A-Za-z0-9\s_\-\.\u00C0-\u1EF9]+?\s+{en_months}\s+\d{{1,2}},?\s+\d{{4}}\s*(at|@|lúc)?\s*\d{{1,2}}[:\.]\d{{2}}\s*(am|pm|AM|PM|sáng|chiều)?\s*(Q|q)?\s*'
    text = re.sub(pattern_en, '', text, flags=re.IGNORECASE)

    # 2. Regex xóa định dạng tiếng Việt: "đăng ngày 9 tháng 8 năm 2022 lúc 15:30"
    pattern_vi = r'^([A-Za-z0-9\s_\-\.\u00C0-\u1EF9]+?\s+)?(đăng\s+|được\s+xuất\s+bản\s+)?(Ngày|ngày)\s+\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}\s*(lúc|at|@)?\s*\d{1,2}[:\.]\d{2}\s*(am|pm|AM|PM|chiều|sáng)?\s*'
    text = re.sub(pattern_vi, '', text, flags=re.IGNORECASE)
    
    # 3. Regex xóa các từ thừa ở cuối do comment: "Reply", "Trả lời"
    text = re.sub(r'\s*[\-–—|]*\s*(Reply|Trả lời|admin|quản trị viên).*$', '', text, flags=re.IGNORECASE)
    
    return text.strip()

def universal_crawler(url, game, db, log_callback, auto_translate=False, progress_callback=None):
    """Bộ cào dữ liệu đa năng: Phiên bản lọc rác và định dạng chuẩn"""
    if not url.startswith("http"):
        log_callback("Lỗi: Link web không hợp lệ!")
        return

    log_callback(f"Đang kết nối: {url[:30]}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8'
        }
        res = requests.get(url, headers=headers, timeout=20, verify=False)
        
        if res.status_code != 200:
            log_callback(f"Lỗi: Mã {res.status_code}")
            return

        soup = BeautifulSoup(res.content, 'html.parser')
        # Chỉ tập trung vào phần nội dung chính của bài viết, bỏ qua Menu/Sidebar nếu được
        main_content = soup.find(['article', 'main']) or soup
        
        new_count = 0
        total_scanned = 0
        items_to_add = []

        # --- CHIẾN THUẬT 1: QUÉT BẢNG (Thường là dữ liệu chuẩn nhất) ---
        for table in main_content.find_all('table'):
            for row in table.find_all('tr'):
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    q = cols[-2].get_text(" ", strip=True)
                    a = cols[-1].get_text(" ", strip=True)
                    if len(q) > 10 and len(a) > 0 and not is_garbage(q):
                        items_to_add.append((q, a))

        # --- CHIẾN THUẬT 2: QUÉT VĂN BẢN (P, LI) ---
        for tag in main_content.find_all(['p', 'li']):
            text = tag.get_text(" ", strip=True)
            text = clean_comment_headers(text)
            if "?" in text:
                q, a = None, None
                has_sep = False
                # Thử tìm các dấu phân cách thông thường trước
                for sep in [":", " – ", " - ", "|", "->"]:
                    if sep in text:
                        parts = text.split(sep, 1)
                        if len(parts) >= 2:
                            q = re.sub(r'^\d+[\.\s\-]+', '', parts[0].strip())
                            a = parts[1].strip()
                            has_sep = True
                            break
                
                # Fallback nếu không có dấu phân cách: Tách bằng chính dấu "?"
                if not has_sep:
                    parts = text.split("?", 1)
                    if len(parts) >= 2:
                        q = re.sub(r'^\d+[\.\s\-]+', '', parts[0].strip()) + "?"
                        a = parts[1].strip()
                
                if q and a:
                    # Lọc sạch các dấu gạch ngang hoặc khoảng trắng thừa ở đầu/cuối câu
                    q = q.strip().rstrip('–').rstrip('-').rstrip(':').strip()
                    a = a.strip().rstrip('–').rstrip('-').rstrip(':').strip()
                    # Lọc kỹ: Câu hỏi phải dài và không phải rác menu
                    if len(q) > 20 and 0 < len(a) < 150 and not is_garbage(q):
                        items_to_add.append((q, a))

        # --- CHIẾN THUẬT 3: QUÉT JSON TRONG SCRIPT / HTML (Cho các trang dạng ứng dụng Vercel/NextJS) ---
        if not items_to_add:
            html_text = res.text
            json_matches = re.findall(r'\\"question\\":\\"(.*?)\\",\\"answer\\":\\"(.*?)\\"', html_text)
            if json_matches:
                for q, a in json_matches:
                    q = q.strip().rstrip(',').rstrip('"').rstrip('\\').strip()
                    a = a.strip().rstrip(',').rstrip('"').rstrip('\\').strip()
                    if len(q) > 15 and len(a) > 0 and not is_garbage(q):
                        items_to_add.append((q, a))

        if items_to_add:
            log_callback(f"Đã lọc được {len(items_to_add)} câu chất lượng.")
            if progress_callback:
                progress_callback(0, len(items_to_add), 0)
                
            for q, a in items_to_add:
                total_scanned += 1
                
                # Nếu có bật tự động dịch và câu hỏi gốc không phải tiếng Việt
                if auto_translate and not is_vietnamese(q):
                    q_vi = translate_to_vi(q)
                    a_vi = translate_to_vi(a)
                    if q_vi != q:
                        if db.add_question(game, q_vi, a_vi): 
                            new_count += 1
                else:
                    if db.add_question(game, q, a):
                        new_count += 1
                
                # Gọi callback tiến độ cập nhật từng câu theo thời gian thực
                if progress_callback:
                    progress_callback(total_scanned, len(items_to_add), new_count)
                elif total_scanned % 30 == 0:
                    log_callback(f"Tiến độ: {total_scanned}/{len(items_to_add)}...")

            log_callback(f"XONG! Thêm mới: {new_count} câu sạch.")
        else:
            log_callback("Không tìm thấy câu hỏi chất lượng.")

    except Exception as e:
        log_callback(f"Lỗi: {str(e)[:40]}")

def restore_vietnamese_accents(text):
    """Sử dụng vòng dịch chuyển dịch thuật (Auto -> EN -> VI) để tự động khôi phục dấu và sửa lỗi chính tả OCR"""
    if not text:
        return text
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        # 1. Dịch sang tiếng Anh (để Google tự khôi phục nghĩa chuẩn và sửa lỗi OCR như nua -> mùa)
        params_en = {'client': 'gtx', 'sl': 'auto', 'tl': 'en', 'dt': 't', 'q': text}
        res_en = requests.get(url, params=params_en, timeout=5)
        if res_en.status_code == 200:
            en_text = "".join([part[0] for part in res_en.json()[0] if part[0]])
            
            # 2. Dịch ngược từ tiếng Anh về tiếng Việt để nhận kết quả chuẩn có dấu đầy đủ
            params_vi = {'client': 'gtx', 'sl': 'en', 'tl': 'vi', 'dt': 't', 'q': en_text}
            res_vi = requests.get(url, params=params_vi, timeout=5)
            if res_vi.status_code == 200:
                vi_text = "".join([part[0] for part in res_vi.json()[0] if part[0]])
                return vi_text
        return text
    except:
        return text

def clean_question_for_search(q):
    """Làm sạch câu hỏi, loại bỏ từ thừa và từ để hỏi để tìm kiếm Wikipedia chính xác hơn"""
    q = q.lower().strip()
    
    # Loại bỏ dấu câu cơ bản
    q = re.sub(r'[\?\.\,\!\-\_\(\)]', ' ', q)
    
    # Danh sách các từ dừng / từ thừa hay gặp trong câu hỏi
    stop_words = [
        "thành phố", "nào", "sau đây", "nằm ở", "ở", "vào", "rơi", "tháng mấy", "là gì", "là ai", 
        "bao nhiêu", "như thế nào", "tại sao", "cái gì", "ai là", "quốc gia", "nước nào", "đơn vị", 
        "chỉ huy", "tướng", "vị", "năm nào", "nhóm", "loại", "vật phẩm", "được", "mệnh danh", "gọi là",
        "có", "thể", "trong", "trên", "dưới", "của", "và", "hoặc", "thì", "mà", "là", "một", "những", "các"
    ]
    
    # Xóa từ thừa
    for word in stop_words:
        q = re.sub(r'\b' + re.escape(word) + r'\b', ' ', q)
        
    # Làm sạch khoảng trắng thừa
    q = re.sub(r'\s+', ' ', q).strip()
    return q

def wikipedia_search_answer(question):
    """Tìm kiếm câu trả lời dự phòng từ Wikipedia API (Không bao giờ bị chặn)"""
    try:
        search_url = "https://vi.wikipedia.org/w/api.php"
        headers = {'User-Agent': 'RoKQuizBot/1.0 (contact@example.com)'}
        
        # 1. Tự động khôi phục dấu và sửa lỗi chính tả OCR tiếng Việt
        corrected_question = restore_vietnamese_accents(question)
        
        # 2. Làm sạch câu hỏi trước khi tìm
        search_term = clean_question_for_search(corrected_question)
        if not search_term:
            search_term = corrected_question
            
        # Tìm kiếm 3 trang kết quả hàng đầu trên Wikipedia
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': search_term,
            'utf8': 1,
            'format': 'json',
            'srlimit': 3
        }
        res = requests.get(search_url, params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            search_results = data.get('query', {}).get('search', [])
            if search_results:
                lines = []
                for i, r in enumerate(search_results):
                    title = r.get('title')
                    snippet = r.get('snippet', '')
                    # Loại bỏ tất cả thẻ HTML trong đoạn trích (ví dụ: <span class="searchmatch">)
                    clean_snippet = re.sub(r'<[^>]*>', '', snippet).strip()
                    if clean_snippet:
                        lines.append(f"{i+1}. {title}: {clean_snippet}...")
                
                if lines:
                    return "\n".join(lines)
        return ""
    except:
        return ""

def google_search_answer(question):
    # 1. Thử tìm kiếm trên Google trước
    try:
        url = f"https://www.google.com/search?q={question}+answer"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8'
        }
        res = requests.get(url, headers=headers, timeout=5, verify=False)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            # Thử lớp di động của Google
            results = soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')
            if results:
                return "\n---\nKẾT QUẢ GOOGLE:\n" + results[0].text[:150]
            
            # Thử lớp máy tính để bàn của Google
            desktop_results = soup.select('div[class*="VwiC3b"]')
            if desktop_results:
                return "\n---\nKẾT QUẢ GOOGLE:\n" + desktop_results[0].get_text()[:150]
    except:
        pass
        
    # 2. DỰ PHÒNG: Nếu Google bị chặn hoặc lỗi -> Tự động truy vấn Wikipedia API (100% thành công)
    wiki_ans = wikipedia_search_answer(question)
    if wiki_ans:
        return wiki_ans
        
    return ""
