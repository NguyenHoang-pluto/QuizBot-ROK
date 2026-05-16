import cv2
import numpy as np

def preprocess_for_ocr(img_np, scale=2.0):
    """Xử lý ảnh để Tesseract đọc chữ tốt nhất"""
    # Chuyển sang ảnh xám
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    
    # Phóng to ảnh (Upscaling)
    if scale != 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Nhị phân hóa (Binarization) dùng Otsu
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary
