import os

# Tự động nạp file .env nếu tồn tại (để lấy đường dẫn cá nhân trên máy local)
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# ĐƯỜNG DẪN HỆ THỐNG
# Tesseract path should be set in .env or as environment variable
TESSERACT_PATH = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
ALI_PATH = os.getenv('ALI_SCRAPED_PATH', "data/ali_content.md")
COD_PATH = os.getenv('COD_SCRAPED_PATH', "data/cod_content.md")
DB_PATH = os.getenv('DB_PATH', "data/rok_quiz.db")
BG_IMAGE_PATH = os.getenv('BG_IMAGE_PATH', os.path.join("assets", "bg.png"))

# CÀI ĐẶT GIAO DIỆN
THEME_MODE = "Dark"
PRIMARY_COLOR = "#ffd700"  # Vàng Gold
SUCCESS_COLOR = "#10b981"  # Xanh lá
DANGER_COLOR = "#ef4444"   # Đỏ
BG_SIDEBAR = "#1a1a1a"

# CÀI ĐẶT LOGIC
MIN_QUESTION_LENGTH = 5
FUZZY_THRESHOLD = 0.75
OCR_LANG = 'vie+eng'
OCR_PSM = 6
IMAGE_UPSCALING = 2.0
