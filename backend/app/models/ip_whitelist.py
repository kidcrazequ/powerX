"""
PowerX IP 白名单模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from app.core.database import Base


class IPWhitelist(Base):
    """IP 白名单"""
    
    __tablename__ = "ip_whitelists"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # IP 地址或 CIDR
    ip_address = Column(String(50), index=True, nullable=False)
    
    # 适用范围
    scope = Column(String(30), default="all")  # all, trading, api, admin
    
    # 用户限制
    user_id = Column(String(50), index=True)  # 空表示所有用户
    
    # 描述
    description = Column(Text)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 有效期
    expires_at = Column(DateTime(timezone=True))
    
    created_by = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IPBlacklist(Base):
    """IP 黑名单"""
    
    __tablename__ = "ip_blacklists"
    
    id = Column(Integer, primary_key=True, index=True)
    
    ip_address = Column(String(50), index=True, nullable=False)
    
    reason = Column(Text)
    
    # 封禁类型
    block_type = Column(String(20), default="permanent")  # permanent, temporary
    
    # 临时封禁的解封时间
    unblock_at = Column(DateTime(timezone=True))
    
    is_active = Column(Boolean, default=True)
    
    created_by = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
