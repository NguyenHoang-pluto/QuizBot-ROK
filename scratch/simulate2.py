import cv2
import pytesseract
import numpy as np

def generate_test_image():
    # Nền light brown (BGR: 140, 180, 210) -> xám ~ 170
    img = np.full((100, 400, 3), (140, 180, 210), dtype=np.uint8)
    
    # Chữ trắng
    cv2.putText(img, 'A Sung tay', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    return img

def test_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # Cũ: global threshold 150
    _, old_bin = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # OTSU INV
    _, otsu_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Adaptive INV C=-10
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, -10)
    
    import sys
    sys.path.append('e:/Tool/QuestionROK')
    from src.core.config import TESSERACT_PATH, OCR_LANG
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    
    methods = {
        "Old (Thresh 150)": old_bin,
        "OTSU INV": otsu_inv,
        "Adaptive INV C=-10": adaptive,
    }
    
    for name, proc in methods.items():
        text = pytesseract.image_to_string(proc, lang=OCR_LANG, config='--psm 7').strip()
        print(f"[{name}]: '{text}'")

img = generate_test_image()
test_ocr(img)
