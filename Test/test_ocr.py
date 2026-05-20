import cv2
import pytesseract
from src.core.config import TESSERACT_PATH
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

img_path = r'e:\Tool\QuestionROK\debug_ocr\opt_b.png'
img_np = cv2.imread(img_path)

gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
scale = 2.0
gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

print("GRAYSCALE:", repr(pytesseract.image_to_string(gray, lang='vie', config='--psm 6').strip()))

# Invert grayscale (if text is white on dark background, invert makes it dark on white background)
inv_gray = cv2.bitwise_not(gray)
print("INV GRAYSCALE:", repr(pytesseract.image_to_string(inv_gray, lang='vie', config='--psm 6').strip()))

# Simple Thresholding
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
print("THRESH BINARY:", repr(pytesseract.image_to_string(thresh, lang='vie', config='--psm 6').strip()))

_, thresh_inv = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
print("THRESH BINARY INV:", repr(pytesseract.image_to_string(thresh_inv, lang='vie', config='--psm 6').strip()))

# OTSU
_, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print("OTSU:", repr(pytesseract.image_to_string(otsu, lang='vie', config='--psm 6').strip()))

_, otsu_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
print("OTSU INV:", repr(pytesseract.image_to_string(otsu_inv, lang='vie', config='--psm 6').strip()))

# Color inversion check: what is the mean brightness?
print("Mean brightness:", gray.mean())
