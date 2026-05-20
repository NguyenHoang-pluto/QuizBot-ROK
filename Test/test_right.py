import cv2
import pytesseract
from src.core.config import TESSERACT_PATH
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

path = r'e:\Tool\QuestionROK\debug_ocr\right_half.png'
img = cv2.imread(path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
_, binary = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY_INV)

text = pytesseract.image_to_string(binary, lang='vie').strip()
print("Right half OCR:")
print(text)
