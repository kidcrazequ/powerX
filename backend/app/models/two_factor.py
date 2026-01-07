"""
PowerX 双因素认证模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class TwoFactorType(str, Enum):
    """2FA 类型"""
    TOTP = "totp"           # 时间一次性密码
    SMS = "sms"             # 短信验证码
    EMAIL = "email"         # 邮件验证码


class TwoFactorConfig(Base):
    """用户双因素认证配置"""
    
    __tablename__ = "two_factor_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    
    # 2FA 类型
    factor_type = Column(String(20), default=TwoFactorType.TOTP.value)
    
    # TOTP 密钥 (加密存储)
    totp_secret = Column(Text)
    
    # 备用码 (JSON 数组)
    backup_codes = Column(Text)
    
    # 是否已启用
    is_enabled = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # 手机号 (短信验证用)
    phone_number = Column(String(20))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True))


class TwoFactorLog(Base):
    """2FA 验证日志"""
    
    __tablename__ = "two_factor_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    factor_type = Column(String(20))
    action = Column(String(50))  # verify, setup, disable
    success = Column(Boolean, default=False)
    
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
