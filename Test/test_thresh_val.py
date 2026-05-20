import cv2
import pytesseract
from src.core.config import TESSERACT_PATH
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

for opt in ['opt_a.png', 'opt_b.png', 'opt_c.png', 'opt_d.png']:
    path = f'e:\\Tool\\QuestionROK\\debug_ocr\\{opt}'
    img = cv2.imread(path)
    if img is None: continue
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # Try different global thresholds
    for thresh_val in [130, 150, 170, 190]:
        _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
        text = pytesseract.image_to_string(binary, lang='vie', config='--psm 7').strip()
        if text:
            print(f"[{opt}] THRESH {thresh_val}: '{text}'")
