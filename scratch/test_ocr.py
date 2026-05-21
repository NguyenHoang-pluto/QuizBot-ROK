import cv2
import pytesseract
import sys
import os
import numpy as np

# Thêm đường dẫn để import được src
sys.path.append('e:/Tool/QuestionROK')
from src.core.config import TESSERACT_PATH, OCR_LANG
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def test_ocr(image_path):
    print(f"Testing {os.path.basename(image_path)}")
    img = cv2.imread(image_path)
    if img is None:
        print("Image not found")
        return
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    methods = {
        "1. threshold 150 INV": cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1],
        "2. threshold 180 INV": cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)[1],
        "3. adaptive threshold": cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10),
        "4. OTSU INV": cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1],
        "5. OTSU": cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        "6. Invert only": cv2.bitwise_not(gray),
    }
    
    for name, proc in methods.items():
        text = pytesseract.image_to_string(proc, lang=OCR_LANG, config='--psm 6').strip()
        print(f"[{name}]: {repr(text)}")

for f in ['opt_a.png', 'opt_b.png']:
    test_ocr(f"e:/Tool/QuestionROK/debug_ocr/{f}")
