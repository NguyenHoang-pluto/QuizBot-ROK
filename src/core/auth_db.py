import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import logging

# Tải cấu hình từ file .env
load_dotenv()

class AuthDB:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "rok_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        
        self.init_db()
        
    def get_connection(self):
        try:
            return psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
        except Exception as e:
            logging.error(f"[AuthDB] Lỗi kết nối PostgreSQL: {e}")
            return None

    def init_db(self):
        """Khởi tạo bảng nếu chưa có."""
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            # Tạo bảng license_keys
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS license_keys (
                    id SERIAL PRIMARY KEY,
                    key_code VARCHAR(255) UNIQUE NOT NULL,
                    role VARCHAR(50) DEFAULT 'user',
                    hwid VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active',
                    price INTEGER DEFAULT 0
                );
            """)
            
            # Kiểm tra xem cột price đã tồn tại chưa (cho CSDL cũ)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='license_keys' and column_name='price';
            """)
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE license_keys ADD COLUMN price INTEGER DEFAULT 0;")
                
            conn.commit()
            cursor.close()
            logging.info("[AuthDB] Đã khởi tạo/cập nhật bảng thành công.")
        except Exception as e:
            logging.error(f"[AuthDB] Lỗi khi tạo bảng: {e}")
        finally:
            conn.close()

    def get_key_info(self, key_code):
        conn = self.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT key_code, role, hwid, expires_at, status 
                FROM license_keys 
                WHERE key_code = %s
            """, (key_code,))
            row = cursor.fetchone()
            if row:
                return {
                    'key_code': row[0],
                    'role': row[1],
                    'hwid': row[2],
                    'expires_at': row[3],
                    'status': row[4]
                }
            return None
        except Exception as e:
            logging.error(f"[AuthDB] Lỗi lấy thông tin key: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def update_hwid(self, key_code, new_hwid):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE license_keys 
                SET hwid = %s 
                WHERE key_code = %s
            """, (new_hwid, key_code))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"[AuthDB] Lỗi cập nhật HWID: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def create_key(self, key_code, role, expires_at=None, price=0):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO license_keys (key_code, role, expires_at, price)
                VALUES (%s, %s, %s, %s)
            """, (key_code, role, expires_at, price))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"[AuthDB] Lỗi tạo key: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def update_key_status(self, key_code, status):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE license_keys 
                SET status = %s 
                WHERE key_code = %s
            """, (status, key_code))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"[AuthDB] Lỗi cập nhật trạng thái key: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def reset_key_hwid(self, key_code):
        return self.update_hwid(key_code, None)

    def get_all_keys(self):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT key_code, role, hwid, expires_at, status, created_at, price
                FROM license_keys
                ORDER BY created_at DESC
            """)
            keys = []
            for row in cursor.fetchall():
                keys.append({
                    'key_code': row[0],
                    'role': row[1],
                    'hwid': row[2],
                    'expires_at': row[3],
                    'status': row[4],
                    'created_at': row[5],
                    'price': row[6]
                })
            return keys
        except Exception as e:
            logging.error(f"[AuthDB] Lỗi lấy danh sách keys: {e}")
            return []
        finally:
            if conn:
                conn.close()
                
    def get_stats(self):
        conn = self.get_connection()
        if not conn:
            return {'total': 0, 'active': 0, 'banned': 0, 'revenue': 0}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM license_keys")
            total = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM license_keys WHERE status = 'active'")
            active = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM license_keys WHERE status = 'banned'")
            banned = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(price) FROM license_keys")
            revenue = cursor.fetchone()[0] or 0
            
            return {
                'total': total,
                'active': active,
                'banned': banned,
                'revenue': revenue
            }
        except Exception as e:
            logging.error(f"[AuthDB] Lỗi lấy thống kê: {e}")
            return {'total': 0, 'active': 0, 'banned': 0, 'revenue': 0}
        finally:
            if conn:
                conn.close()
