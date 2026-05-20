import cv2
import pytesseract
from src.core.config import TESSERACT_PATH
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
import os

for opt in ['opt_a.png', 'opt_b.png', 'opt_c.png', 'opt_d.png']:
    path = f'e:\\Tool\\QuestionROK\\debug_ocr\\{opt}'
    img = cv2.imread(path)
    if img is None: continue
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # 1. Threshold for bright text (white/light yellow)
    # Background is tan, which is around 120-170 in grayscale.
    # Text is bright white, which is > 200.
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    
    # 2. Invert so text is black, background is white
    binary_inv = cv2.bitwise_not(binary)
    
    # Optional: thin the text if it's too thick due to scaling? No, let's just try.
    text = pytesseract.image_to_string(binary_inv, lang='vie', config='--psm 7').strip()
    print(f"[{opt}] THRESH 180 INV: '{text}'")
    
    # Let's save it to see visually later if needed
    cv2.imwrite(f'e:\\Tool\\QuestionROK\\debug_ocr\\thresh_{opt}', binary_inv)
