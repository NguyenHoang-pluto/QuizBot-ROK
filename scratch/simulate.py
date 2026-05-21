import cv2
import pytesseract
import numpy as np

def generate_test_image():
    # Nền light brown (BGR: 140, 180, 210) -> xám ~ 170
    img = np.full((100, 400, 3), (140, 180, 210), dtype=np.uint8)
    
    # Chữ trắng
    cv2.putText(img, 'A Sung tay', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    # Lưu lại để xem bằng mắt
    cv2.imwrite('e:/Tool/QuestionROK/scratch/dummy_answer.png', img)
    return img

def test_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Phóng to
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # Cũ: global threshold 150
    _, old_bin = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    cv2.imwrite('e:/Tool/QuestionROK/scratch/old_bin.png', old_bin)
    
    # Cũ nhưng threshold 200 (để tránh nền xám 170)
    _, old_bin_200 = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    cv2.imwrite('e:/Tool/QuestionROK/scratch/old_bin_200.png', old_bin_200)
    
    # Mới: adaptive THRESH_BINARY_INV, blockSize=31, C=10 (hoặc -10)
    # T(x,y) = mean - C
    # dst = 0 if src > T else 255
    new_bin_posC = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 10)
    cv2.imwrite('e:/Tool/QuestionROK/scratch/new_bin_posC.png', new_bin_posC)
    
    new_bin_negC = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, -10)
    cv2.imwrite('e:/Tool/QuestionROK/scratch/new_bin_negC.png', new_bin_negC)
    
    new_bin_posC_INV = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, -10)
    cv2.imwrite('e:/Tool/QuestionROK/scratch/new_bin_posC_INV.png', new_bin_posC_INV)
    
    import sys
    sys.path.append('e:/Tool/QuestionROK')
    from src.core.config import TESSERACT_PATH, OCR_LANG
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    
    methods = {
        "Old (Thresh 150)": old_bin,
        "Old (Thresh 200)": old_bin_200,
        "Adaptive INV C=10": new_bin_posC,
        "Adaptive INV C=-10": new_bin_negC,
        "Adaptive C=-10": new_bin_posC_INV,
    }
    
    for name, proc in methods.items():
        text = pytesseract.image_to_string(proc, lang=OCR_LANG, config='--psm 7').strip()
        print(f"[{name}]: '{text}'")

img = generate_test_image()
test_ocr(img)
