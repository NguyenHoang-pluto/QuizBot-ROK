import platform
import subprocess
import os
import uuid
import hashlib
import random
import string
from datetime import datetime, timedelta
from src.core.auth_db import AuthDB

class AuthManager:
    def __init__(self):
        self.db = AuthDB()

    def get_hardware_id(self):
        """Lấy thông tin HWID (khóa theo thiết bị)."""
        system = platform.system()
        hwid_str = ""
        try:
            if system == "Windows":
                # Lấy UUID của máy trên Windows
                output = subprocess.check_output("wmic csproduct get uuid", shell=True).decode()
                hwid_str = output.split('\n')[1].strip()
            elif system == "Darwin":
                # MacOS
                output = subprocess.check_output("ioreg -l | grep IOPlatformSerialNumber", shell=True).decode()
                hwid_str = output.split('"')[3]
            elif system == "Linux":
                # Linux (đòi hỏi root, hoặc lấy product_uuid)
                try:
                    with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                        hwid_str = f.read().strip()
                except:
                    with open('/etc/machine-id', 'r') as f:
                        hwid_str = f.read().strip()
        except Exception:
            # Fallback nếu lỗi
            hwid_str = str(uuid.getnode())

        # Hash để bảo mật
        return hashlib.sha256(hwid_str.encode('utf-8')).hexdigest()

    def login(self, key_code):
        """Xử lý đăng nhập."""
        admin_key = os.getenv("ADMIN_KEY", "ADMIN-ROK-VIP")
        if key_code == admin_key:
            return {"success": True, "role": "admin", "message": "Đăng nhập Admin thành công"}
            
        key_info = self.db.get_key_info(key_code)
        
        if not key_info:
            return {"success": False, "message": "Key không tồn tại hoặc sai"}
            
        if key_info['status'] == 'banned':
            return {"success": False, "message": "Key này đã bị khóa (banned)"}
            
        # Kiểm tra hạn
        if key_info['expires_at']:
            # Đảm bảo expires_at là datetime (psycopg2 thường trả về datetime)
            now = datetime.now()
            if key_info['expires_at'] < now:
                self.db.update_key_status(key_code, 'expired')
                return {"success": False, "message": "Key này đã hết hạn"}
                
        hwid = self.get_hardware_id()
        
        if not key_info['hwid']:
            # Khóa HWID vào key cho lần đầu
            if self.db.update_hwid(key_code, hwid):
                return {"success": True, "role": key_info['role'], "message": "Đăng nhập thành công! Key đã được gắn với thiết bị này."}
            else:
                return {"success": False, "message": "Lỗi kết nối cơ sở dữ liệu khi gắn HWID"}
                
        if key_info['hwid'] != hwid:
            return {"success": False, "message": "Key này đã được sử dụng trên một thiết bị khác!"}
            
        return {"success": True, "role": key_info['role'], "message": "Đăng nhập thành công"}

    def generate_key(self, prefix="ROK", duration_days=None, price=0):
        """Tạo mã bản quyền ngẫu nhiên (dùng cho Admin)"""
        # Tạo chuỗi ngẫu nhiên dạng AAAA-BBBB-CCCC
        random_part = '-'.join([''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3)])
        new_key = f"{prefix}-{random_part}"
        
        expires_at = None
        if duration_days:
            expires_at = datetime.now() + timedelta(days=duration_days)
            
        success = self.db.create_key(new_key, "user", expires_at, price=price)
        return new_key if success else None
