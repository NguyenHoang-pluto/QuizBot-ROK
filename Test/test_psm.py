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
    
    # Try different PSMs
    text_psm6 = pytesseract.image_to_string(gray, lang='vie', config='--psm 6').strip()
    text_psm7 = pytesseract.image_to_string(gray, lang='vie', config='--psm 7').strip()
    
    # Also try just THRESH_BINARY with large block size
    # If text is white with black outline, maybe invert the image first
    inv_gray = cv2.bitwise_not(gray)
    text_inv_psm7 = pytesseract.image_to_string(inv_gray, lang='vie', config='--psm 7').strip()
    
    print(f"[{opt}] GRAY PSM6: '{text_psm6}'")
    print(f"[{opt}] GRAY PSM7: '{text_psm7}'")
    print(f"[{opt}] INV_GRAY PSM7: '{text_inv_psm7}'")
