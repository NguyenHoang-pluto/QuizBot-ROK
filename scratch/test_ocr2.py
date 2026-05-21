import cv2
import pytesseract
import sys
import os
import numpy as np

sys.path.append('e:/Tool/QuestionROK')
from src.core.config import TESSERACT_PATH, OCR_LANG
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def test_ocr(image_path):
    print(f"Testing {os.path.basename(image_path)}")
    img = cv2.imread(image_path)
    if img is None:
        return
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    methods = {
        "adaptive THRESH_BINARY_INV": cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, -10),
        "adaptive THRESH_BINARY_INV 2": cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 10),
        "adaptive THRESH_BINARY": cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10),
        "adaptive THRESH_BINARY C=-10": cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, -10),
    }
    
    for name, proc in methods.items():
        text = pytesseract.image_to_string(proc, lang=OCR_LANG, config='--psm 6').strip()
        print(f"[{name}]: {repr(text)}")

for f in ['opt_a.png']:
    test_ocr(f"e:/Tool/QuestionROK/debug_ocr/{f}")
