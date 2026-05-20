import cv2
import pytesseract
from src.core.config import TESSERACT_PATH
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def preprocess_option(img_path):
    img_np = cv2.imread(img_path)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    scale = 2.0
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # 1. THRESH_BINARY_INV to make white text black
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 8
    )
    
    # Optional: no morphology or MORPH_OPEN (if text is black, open removes white noise)
    # Wait, if text is black (0) on white background (255), 
    # MORPH_OPEN removes small white regions (noise on the black text).
    # MORPH_CLOSE removes small black regions (noise on the white background).
    
    text1 = pytesseract.image_to_string(binary, lang='vie', config='--psm 6').strip()
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    # Try OPEN
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    text2 = pytesseract.image_to_string(opened, lang='vie', config='--psm 6').strip()
    
    # Try CLOSE
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    text3 = pytesseract.image_to_string(closed, lang='vie', config='--psm 6').strip()
    
    print(f"[{img_path}] RAW BINARY INV: '{text1}'")
    print(f"[{img_path}] OPENED: '{text2}'")
    print(f"[{img_path}] CLOSED: '{text3}'")

for opt in ['opt_a.png', 'opt_b.png', 'opt_c.png', 'opt_d.png']:
    preprocess_option(f'e:\\Tool\\QuestionROK\\debug_ocr\\{opt}')
