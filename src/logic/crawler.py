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

def universal_crawler(url, game, db, log_callback, auto_translate=False):
    """Bộ cào dữ liệu đa năng: Phiên bản lọc rác và định dạng chuẩn"""
    if not url.startswith("http"):
        log_callback("Lỗi: Link web không hợp lệ!")
        return

    log_callback(f"Đang kết nối: {url[:30]}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
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
            for sep in [":", " – ", " - ", "|", "->"]:
                if "?" in text and sep in text:
                    parts = text.split(sep)
                    if len(parts) >= 2:
                        q = re.sub(r'^\d+[\.\s\-]+', '', parts[0].strip())
                        a = parts[1].strip()
                        # Lọc kỹ: Câu hỏi phải dài và không phải rác menu
                        if len(q) > 20 and 0 < len(a) < 150 and not is_garbage(q):
                            items_to_add.append((q, a))
                            break

        if items_to_add:
            log_callback(f"Đã lọc được {len(items_to_add)} câu chất lượng.")
            for q, a in items_to_add:
                total_scanned += 1
                
                # Bản gốc
                if db.add_question(game, q, a):
                    new_count += 1
                
                if auto_translate and not is_vietnamese(q):
                    q_vi = translate_to_vi(q); a_vi = translate_to_vi(a)
                    if q_vi != q:
                        if db.add_question(game, q_vi, a_vi): new_count += 1
                
                if total_scanned % 30 == 0:
                    log_callback(f"Tiến độ: {total_scanned}/{len(items_to_add)}...")

            log_callback(f"XONG! Thêm mới: {new_count} câu sạch.")
        else:
            log_callback("Không tìm thấy câu hỏi chất lượng.")

    except Exception as e:
        log_callback(f"Lỗi: {str(e)[:40]}")

def google_search_answer(question):
    try:
        url = f"https://www.google.com/search?q={question}+answer"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5, verify=False)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            results = soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')
            if results:
                return "\n---\nKẾT QUẢ GOOGLE:\n" + results[0].text[:150]
        return ""
    except: return ""
