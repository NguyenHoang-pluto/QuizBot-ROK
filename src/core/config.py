import os

# ĐƯỜNG DẪN HỆ THỐNG
TESSERACT_PATH = r'E:\LibTool\tesseract.exe'
DB_PATH = "data/rok_quiz.db"
BG_IMAGE_PATH = os.path.join("assets", "bg.png")

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
