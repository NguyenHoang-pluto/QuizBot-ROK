import cv2
import numpy as np

def preprocess_for_ocr(img_np, scale=2.0):
    """Xử lý ảnh để Tesseract đọc chữ tốt nhất - Tối ưu cho game ROK/COD"""
    if img_np is None or img_np.size == 0:
        return img_np
    
    # Chuyển từ BGRA (mss output) sang BGR nếu cần
    if len(img_np.shape) == 3 and img_np.shape[2] == 4:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    
    # Chuyển sang ảnh xám
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_np.copy()
    
    # Phóng to ảnh (Upscaling) trước khi xử lý
    if scale != 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Adaptive thresholding: chuyển nền sáng thành trắng, chữ tối thành đen
    # Phù hợp hơn equalizeHist cho text trên nền game đa dạng
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    
    # Khử nhiễu nhẹ bằng morphological opening (loại bỏ hạt pixel nhỏ)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    return cleaned


def preprocess_option_for_ocr(img_np, scale=2.0):
    """Xử lý ảnh đặc biệt cho đáp án game - tối ưu cho dòng text ngắn"""
    if img_np is None or img_np.size == 0:
        return img_np
    
    # Chuyển từ BGRA (mss output) sang BGR nếu cần
    if len(img_np.shape) == 3 and img_np.shape[2] == 4:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    
    # Chuyển sang ảnh xám
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_np.copy()
    
    # Phóng to ảnh
    if scale != 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Dùng global threshold THRESH_BINARY_INV vì chữ đáp án game thường màu trắng
    # Điều này sẽ làm chữ trắng thành đen (0) và nền thành trắng (255)
    # Tesseract đọc chữ đen trên nền trắng chính xác nhất. Ngưỡng 150-180 là tối ưu.
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    return binary
