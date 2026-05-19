import re

def clean_comment_headers(text):
    if not text:
        return text
    
    # 1. Regex xóa định dạng thời gian tiếng Anh: "Name August 8, 2022 at 12:45 am" hoặc "Name September 6, 2022 at 5:14 pm Q"
    en_months = "(January|February|March|April|May|June|July|August|September|October|November|December)"
    pattern_en = rf'^[A-Za-z0-9\s_\-\.\u00C0-\u1EF9]+?\s+{en_months}\s+\d{{1,2}},?\s+\d{{4}}\s*(at|@|lúc)?\s*\d{{1,2}}[:\.]\d{{2}}\s*(am|pm|AM|PM|sáng|chiều)?\s*(Q|q)?\s*'
    text = re.sub(pattern_en, '', text, flags=re.IGNORECASE)

    # 2. Regex xóa định dạng tiếng Việt: "đăng ngày 9 tháng 8 năm 2022 lúc 15:30" hoặc "Name Ngày 3 tháng 10 năm 2022 lúc 2:39"
    pattern_vi = r'^([A-Za-z0-9\s_\-\.\u00C0-\u1EF9]+?\s+)?(đăng\s+|được\s+xuất\s+bản\s+)?(Ngày|ngày)\s+\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}\s*(lúc|at|@)?\s*\d{1,2}[:\.]\d{2}\s*(am|pm|AM|PM|chiều|sáng)?\s*'
    text = re.sub(pattern_vi, '', text, flags=re.IGNORECASE)
    
    # 3. Regex xóa các từ thừa ở cuối do comment: "Reply", "Trả lời", v.v. kèm theo gạch ngang đứng trước
    text = re.sub(r'\s*[\-–—|]*\s*(Reply|Trả lời|admin|quản trị viên).*$', '', text, flags=re.IGNORECASE)
    
    return text.strip()

# Các test cases từ database thực tế bị lỗi
test_cases = [
    "elmantaokuro August 8, 2022 at 12:45 am What age did ancient greece enter after the mycenaean civilization was destroyed? Dark Age Reply admin August 9, 2022 at 8",
    "elmentao kuro August 9, 2022 at 3:15 am Which of the following civilization can increase their healing speed? FRANCE Reply",
    "Moosa September 6, 2022 at 5:14 pm Q What age did ancient greece enter?",
    "Josh Ngày 3 tháng 10 năm 2022 lúc 2:39 chiều In what year did the Late Show with David Letterman first premier? 1993 Reply",
    "đăng ngày 9 tháng 8 năm 2022 lúc 15:30 Nền văn minh nào sau đây có thể tăng tốc độ chữa bệnh? PHÁP Trả lời",
    "được xuất bản ngày 11 tháng 8 năm 2022 lúc 15:00 Thủ lĩnh nào trong sự kiện Khủng hoảng Ceroli đã đảo chính thành công? – Trả lời khó chịu"
]

print("--- KẾT QUẢ TEST CLEANER TỐI ƯU ---")
for i, tc in enumerate(test_cases):
    cleaned = clean_comment_headers(tc)
    print(f"\n{i+1}. GỐC: {repr(tc)}")
    print(f"   SẠCH: {repr(cleaned)}")
