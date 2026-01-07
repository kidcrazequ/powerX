"""
PowerX 跨省交易订单模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class CrossProvinceOrderStatus(str, Enum):
    """跨省订单状态"""
    PENDING = "pending"
    MATCHING = "matching"
    MATCHED = "matched"
    PARTIAL = "partial"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class CrossProvinceOrder(Base):
    """跨省交易订单"""
    
    __tablename__ = "cross_province_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True)
    
    user_id = Column(String(50), index=True, nullable=False)
    
    # 交易方向
    order_type = Column(String(10))  # buy, sell
    
    # 来源省份
    source_province = Column(String(20), index=True)
    # 目标省份
    target_province = Column(String(20), index=True)
    
    # 输电通道
    transmission_channel = Column(String(50))
    
    # 交易量
    quantity = Column(Float, nullable=False)  # MWh
    filled_quantity = Column(Float, default=0)
    
    # 价格
    price = Column(Float)  # 报价
    transmission_fee = Column(Float, default=0)  # 输电费
    total_price = Column(Float)  # 总价
    
    # 交割时间
    delivery_start = Column(DateTime(timezone=True))
    delivery_end = Column(DateTime(timezone=True))
    
    # 状态
    status = Column(String(20), default=CrossProvinceOrderStatus.PENDING.value)
    
    # 匹配信息
    matched_order_id = Column(String(50))
    match_time = Column(DateTime(timezone=True))
    
    # 额外信息
    notes = Column(Text)
    metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TransmissionChannel(Base):
    """输电通道"""
    
    __tablename__ = "transmission_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    
    channel_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    
    # 起止省份
    from_province = Column(String(20), index=True)
    to_province = Column(String(20), index=True)
    
    # 容量
    capacity = Column(Float)  # 最大输电容量 MW
    available_capacity = Column(Float)  # 可用容量
    
    # 费用
    transmission_fee = Column(Float)  # 元/MWh
    
    # 线损率
    loss_rate = Column(Float, default=0.03)  # 3%
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
