"""
PowerX 加密工具
创建日期: 2026-01-07
作者: zhi.qu
"""
import base64
import hashlib
import secrets
from loguru import logger


class EncryptionService:
    """加密服务"""
    
    def __init__(self):
        self._key = secrets.token_bytes(32)
        logger.info("EncryptionService 初始化完成")
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            salt, hash_value = hashed.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_value
        except Exception:
            return False
    
    @staticmethod
    def mask_email(email: str) -> str:
        """脱敏邮箱"""
        if not email or '@' not in email:
            return email
        local, domain = email.split('@')
        return f"{local[0]}***@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """脱敏手机号"""
        if not phone or len(phone) < 7:
            return phone
        return phone[:3] + '****' + phone[-4:]
    
    def generate_api_key(self) -> str:
        """生成 API 密钥"""
        return f"pk_{secrets.token_urlsafe(32)}"


encryption_service = EncryptionService()


def get_encryption_service() -> EncryptionService:
    return encryption_service
