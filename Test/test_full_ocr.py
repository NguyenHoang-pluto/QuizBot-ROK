import cv2
import pytesseract
from src.core.config import TESSERACT_PATH
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

img_path = r'e:\Tool\QuestionROK\debug_ocr\full.png'
img_np = cv2.imread(img_path)

gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
scale = 2.0
gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

text = pytesseract.image_to_string(gray, lang='vie').strip()
print("FULL IMAGE OCR GRAY:")
print(text)

# Also test with adaptive threshold from preprocess_for_ocr
binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
text_bin = pytesseract.image_to_string(binary, lang='vie').strip()
print("FULL IMAGE OCR BINARY:")
print(text_bin)
