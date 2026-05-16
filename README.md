# 🛡️ QuizBot-ROK (Rise of Kingdoms Quiz Helper)

Công cụ hỗ trợ giải đố thông minh cho game **Rise of Kingdoms** và **Call of Dragons**. Tích hợp công nghệ OCR, tìm kiếm mờ (Fuzzy Search) và bộ cào dữ liệu tự động.

## ✨ Tính năng nổi bật
- 🔍 **Tìm kiếm thông minh**: Sử dụng thuật toán Fuzzy Matching để tìm câu trả lời ngay cả khi từ khóa không khớp hoàn toàn.
- 📸 **OCR Screenshot**: Tự động đọc câu hỏi từ ảnh chụp màn hình (hỗ trợ Bluestacks/LDPlayer).
- 🌐 **Auto Crawler**: Tự động thu thập dữ liệu câu hỏi từ các trang web lớn như Ali213, Cod.guide...
- 🗂️ **Database Manager**: Quản lý kho câu hỏi khổng lồ, hỗ trợ import từ Excel/CSV.
- 🎨 **Giao diện hiện đại**: Chế độ Dark Mode chuyên nghiệp, tối ưu cho game thủ.

## 🛠️ Yêu cầu hệ thống
- Python 3.8+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (Để dùng tính năng đọc ảnh)

## 🚀 Cài đặt

1. **Clone dự án:**
   ```bash
   git clone https://github.com/NguyenHoang-pluto/QuizBot-ROK.git
   cd QuizBot-ROK
   ```

2. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Nếu chưa có file requirements.txt, hãy cài: `pip install requests beautifulsoup4 opencv-python pytesseract customtkinter pillow`) archaeology*

3. **Cấu hình Tesseract:**
   Tải và cài đặt Tesseract OCR, sau đó ghi nhớ đường dẫn file `tesseract.exe`.

## ⚙️ Cấu hình (.env)
Để đảm bảo bảo mật và chạy được trên máy cá nhân, hãy tạo file `.env` tại thư mục gốc và cấu hình như sau:

```env
# Đường dẫn tới file tesseract.exe trên máy bạn
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# (Tùy chọn) Đường dẫn database
DB_PATH=data/rok_quiz.db
```

## 📖 Cách sử dụng

1. **Chạy ứng dụng chính:**
   ```bash
   python main.py
   ```

2. **Import dữ liệu từ Excel:**
   ```bash
   python import_excel.py
   ```

3. **Cào dữ liệu mới từ web:**
   Chạy tính năng Crawler ngay trên giao diện chính hoặc thông qua script `import_scraped.py`.

## 🔒 Bảo mật
Dự án sử dụng cơ chế `.env` để bảo vệ thông tin cá nhân. Vui lòng không push file `.env` lên GitHub (đã được chặn trong `.gitignore`).

---
*Phát triển bởi [NguyenHoang-pluto](https://github.com/NguyenHoang-pluto)*
