import mss
import numpy as np
import cv2
import pytesseract
import os
from src.core.config import TESSERACT_PATH, IMAGE_UPSCALING, OCR_LANG, OCR_PSM
from src.utils.image_proc import preprocess_for_ocr

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def test_capture():
    print("--- CHƯƠNG TRÌNH CHẨN ĐOÁN LỖI NHẬN DIỆN ---")
    print(f"1. Kiểm tra file tesseract.exe:")
    print(f"   Đường dẫn cấu hình: {TESSERACT_PATH}")
    if os.path.exists(TESSERACT_PATH):
        print("   => [OK] Tìm thấy file tesseract.exe!")
    else:
        print("   => [LỖI] Không tìm thấy file tesseract.exe tại đường dẫn trên!")
        print("      Vui lòng cài đặt Tesseract OCR hoặc kiểm tra lại cấu hình đường dẫn.")
        return

    # Tọa độ từ ảnh chụp màn hình của bạn
    # X=675, Y=381, W=376, chúng ta chọn đại diện H=40
    x, y, w, h = 675, 381, 376, 40
    print(f"\n2. Thử chụp vùng màn hình: X={x}, Y={y}, W={w}, H={h}")
    
    try:
        sct = mss.mss()
        monitor = {"top": y, "left": x, "width": w, "height": h}
        sct_img = sct.grab(monitor)
        img_np = np.array(sct_img)
        
        # Lưu ảnh gốc chụp được
        cv2.imwrite("debug_raw.png", img_np)
        print("   => [OK] Đã lưu ảnh chụp màn hình gốc vào file 'debug_raw.png'")
        
        # Xử lý ảnh
        processed_img = preprocess_for_ocr(img_np, scale=IMAGE_UPSCALING)
        cv2.imwrite("debug_processed.png", processed_img)
        print("   => [OK] Đã lưu ảnh sau xử lý vào file 'debug_processed.png'")
        
        # Thử nhận diện chữ bằng Tesseract
        print("\n3. Thử nhận diện chữ bằng Tesseract OCR...")
        text = pytesseract.image_to_string(processed_img, lang=OCR_LANG, config=f'--psm {OCR_PSM}').strip()
        
        print(f"   => Kết quả OCR nhận diện được: '{text}'")
        if not text:
            print("   => [CẢNH BÁO] Kết quả trống! Có thể vùng chụp bị lệch hoặc ảnh không chứa chữ rõ ràng.")
            
    except Exception as e:
        print(f"   => [LỖI CỰC KỲ NGHIÊM TRỌNG]: {e}")

if __name__ == "__main__":
    test_capture()
