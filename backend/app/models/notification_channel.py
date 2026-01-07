"""
PowerX 通知渠道数据模型

创建日期: 2026-01-07
作者: zhi.qu

定义通知渠道和通知记录相关的数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ChannelType(str, enum.Enum):
    """通知渠道类型"""
    EMAIL = "EMAIL"
    WECHAT = "WECHAT"
    DINGTALK = "DINGTALK"
    SMS = "SMS"
    WEBHOOK = "WEBHOOK"


class NotificationChannel(Base):
    """通知渠道配置"""
    
    __tablename__ = "notification_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # 渠道信息
    channel_type = Column(String(20), nullable=False)
    channel_name = Column(String(100), nullable=False)
    
    # 配置
    config = Column(JSON, default=dict)  # 渠道配置(加密存储敏感信息)
    
    # 启用状态
    is_enabled = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # 是否已验证
    
    # 通知偏好
    notify_on_trade = Column(Boolean, default=True)
    notify_on_alert = Column(Boolean, default=True)
    notify_on_approval = Column(Boolean, default=True)
    notify_on_system = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NotificationRecord(Base):
    """通知发送记录"""
    
    __tablename__ = "notification_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    channel_type = Column(String(20), nullable=False)
    
    # 通知内容
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    notification_type = Column(String(50), nullable=True)  # trade/alert/approval/system
    
    # 发送状态
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # 关联
    related_id = Column(String, nullable=True)  # 关联的业务ID
    related_type = Column(String(50), nullable=True)  # 关联的业务类型
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
