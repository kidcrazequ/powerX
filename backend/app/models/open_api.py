"""
PowerX 开放 API 模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class APIKeyStatus(str, Enum):
    """API 密钥状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"


class APIKey(Base):
    """API 密钥"""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String(50), unique=True, index=True)
    
    user_id = Column(String(50), index=True)
    
    name = Column(String(100))
    description = Column(Text)
    
    # 密钥
    api_key = Column(String(100), unique=True, index=True)
    api_secret = Column(String(100))  # 哈希存储
    
    # 权限
    permissions = Column(JSON)  # 允许的操作列表
    
    # IP 限制
    allowed_ips = Column(JSON)  # 允许的 IP 列表
    
    # 速率限制
    rate_limit = Column(Integer, default=1000)  # 每小时请求数
    
    # 状态
    status = Column(String(20), default=APIKeyStatus.ACTIVE.value)
    
    # 有效期
    expires_at = Column(DateTime(timezone=True))
    
    # 统计
    request_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class APIUsageLog(Base):
    """API 使用日志"""
    
    __tablename__ = "api_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    key_id = Column(String(50), index=True)
    
    # 请求信息
    endpoint = Column(String(200))
    method = Column(String(10))
    request_ip = Column(String(50))
    
    # 响应
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    
    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
