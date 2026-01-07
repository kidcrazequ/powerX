"""
PowerX 组合订单模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.database import Base


class ComboOrderStatus(str, Enum):
    """组合订单状态"""
    DRAFT = "draft"             # 草稿
    PENDING = "pending"         # 待提交
    SUBMITTED = "submitted"     # 已提交
    PARTIAL = "partial"         # 部分成交
    FILLED = "filled"           # 全部成交
    CANCELLED = "cancelled"     # 已取消
    FAILED = "failed"           # 失败


class ComboExecutionStrategy(str, Enum):
    """执行策略"""
    ALL_OR_NONE = "all_or_none"   # 全部成交或取消
    PARTIAL_OK = "partial_ok"     # 允许部分成交
    BEST_EFFORT = "best_effort"   # 尽力成交


class ComboOrder(Base):
    """组合订单"""
    
    __tablename__ = "combo_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    combo_id = Column(String(50), unique=True, index=True, nullable=False)
    
    user_id = Column(String, index=True, nullable=False)
    name = Column(String(100))  # 组合名称
    description = Column(Text)
    
    # 执行策略
    execution_strategy = Column(String(30), default=ComboExecutionStrategy.ALL_OR_NONE.value)
    
    # 状态
    status = Column(String(20), default=ComboOrderStatus.DRAFT.value)
    
    # 统计
    total_orders = Column(Integer, default=0)
    filled_orders = Column(Integer, default=0)
    total_quantity = Column(Float, default=0)
    total_amount = Column(Float, default=0)
    
    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # 关联子订单
    items = relationship("ComboOrderItem", back_populates="combo_order", cascade="all, delete-orphan")


class ComboOrderItem(Base):
    """组合订单子项"""
    
    __tablename__ = "combo_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    combo_order_id = Column(Integer, ForeignKey("combo_orders.id"), nullable=False)
    
    # 订单信息
    order_id = Column(String(50), unique=True, index=True)  # 实际订单ID
    
    # 交易信息
    province = Column(String(20))
    market_type = Column(String(20))  # spot, mid_long
    order_type = Column(String(10))   # buy, sell
    
    quantity = Column(Float, nullable=False)  # MWh
    price = Column(Float)  # 元/MWh
    
    # 状态
    status = Column(String(20), default="pending")
    filled_quantity = Column(Float, default=0)
    filled_price = Column(Float)
    
    # 优先级 (执行顺序)
    priority = Column(Integer, default=0)
    
    # 错误信息
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))
    
    # 关联
    combo_order = relationship("ComboOrder", back_populates="items")
