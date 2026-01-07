"""
PowerX Webhook 模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class WebhookEvent(str, Enum):
    """Webhook 事件"""
    ORDER_CREATED = "order.created"
    ORDER_FILLED = "order.filled"
    ORDER_CANCELLED = "order.cancelled"
    PRICE_ALERT = "price.alert"
    RISK_WARNING = "risk.warning"
    SYSTEM_NOTICE = "system.notice"


class Webhook(Base):
    """Webhook 配置"""
    
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(String(50), unique=True, index=True)
    
    user_id = Column(String(50), index=True)
    
    name = Column(String(100))
    url = Column(String(500), nullable=False)
    
    # 订阅的事件
    events = Column(JSON)  # 事件列表
    
    # 密钥
    secret = Column(String(100))
    
    # 请求头
    headers = Column(JSON)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 统计
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime(timezone=True))
    last_status = Column(String(20))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WebhookLog(Base):
    """Webhook 日志"""
    
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    webhook_id = Column(String(50), index=True)
    event = Column(String(50), index=True)
    
    # 请求
    request_body = Column(JSON)
    
    # 响应
    response_status = Column(Integer)
    response_body = Column(Text)
    
    # 耗时
    duration_ms = Column(Integer)
    
    # 结果
    success = Column(Boolean)
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
