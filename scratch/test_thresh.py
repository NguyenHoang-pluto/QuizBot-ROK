import cv2
import pytesseract
import numpy as np
import sys
import os

sys.path.append('e:/Tool/QuestionROK')
from src.core.config import TESSERACT_PATH, OCR_LANG
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def generate_test_images():
    # Giả lập 1 vùng đáp án với vân giấy da (thay đổi độ sáng một chút để có gradient)
    img = np.zeros((80, 300, 3), dtype=np.uint8)
    for x in range(300):
        for y in range(80):
            # Nền nâu vàng, sáng dần từ trái sang phải
            v = 150 + int((x/300)*30) + np.random.randint(-5, 5)
            img[y, x] = [max(0, v-40), v-10, v+20] # BGR cho màu nâu vàng nhạt
            
    # Vẽ chữ trắng (màu 255) - mô phỏng nét dày
    cv2.putText(img, 'B 3', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
    cv2.putText(img, 'D 4', (150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
    
    cv2.imwrite('e:/Tool/QuestionROK/scratch/mock_game.png', img)
    return img

def test_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # Phương pháp 1: Adaptive 31, C=-10 (Hiện tại)
    bin_adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, -10)
    
    # Phương pháp 2: Mean + offset
    mean_val = cv2.mean(gray)[0]
    thresh_val = mean_val + 30
    _, bin_mean = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
    
    # Phương pháp 3: Adaptive nhưng blockSize lớn hơn (91), C=-10
    bin_adapt_91 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 91, -10)
    
    methods = {
        "Adaptive 31": bin_adapt,
        "Mean + 30": bin_mean,
        "Adaptive 91": bin_adapt_91
    }
    
    for name, proc in methods.items():
        # Pad viền
        proc = cv2.copyMakeBorder(proc, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
        text = pytesseract.image_to_string(proc, lang=OCR_LANG, config='--psm 6').strip()
        print(f"[{name}]: '{text}'")
        cv2.imwrite(f'e:/Tool/QuestionROK/scratch/{name.replace(" ", "_")}.png', proc)

test_ocr(generate_test_images())
