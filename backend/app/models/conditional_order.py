"""
PowerX 条件单数据模型

创建日期: 2026-01-07
作者: zhi.qu

定义条件单和触发条件相关的数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class ConditionType(str, enum.Enum):
    """条件类型"""
    PRICE_ABOVE = "PRICE_ABOVE"           # 价格高于
    PRICE_BELOW = "PRICE_BELOW"           # 价格低于
    PRICE_CHANGE_PCT = "PRICE_CHANGE_PCT" # 价格变动百分比
    TIME_TRIGGER = "TIME_TRIGGER"         # 时间触发
    VOLUME_ABOVE = "VOLUME_ABOVE"         # 成交量高于
    INDICATOR = "INDICATOR"               # 技术指标


class ConditionStatus(str, enum.Enum):
    """条件单状态"""
    PENDING = "PENDING"       # 等待触发
    TRIGGERED = "TRIGGERED"   # 已触发
    EXECUTED = "EXECUTED"     # 已执行
    CANCELLED = "CANCELLED"   # 已取消
    EXPIRED = "EXPIRED"       # 已过期
    FAILED = "FAILED"         # 执行失败


class OrderDirection(str, enum.Enum):
    """订单方向"""
    BUY = "BUY"
    SELL = "SELL"


class ConditionalOrder(Base):
    """条件单"""
    
    __tablename__ = "conditional_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String(200), nullable=True)  # 条件单名称
    
    # 触发条件
    condition_type = Column(String(50), nullable=False)
    province = Column(String(50), nullable=False)  # 适用省份
    market_type = Column(String(50), default="DAY_AHEAD")  # 市场类型
    
    # 条件参数
    trigger_price = Column(Float, nullable=True)  # 触发价格
    trigger_change_pct = Column(Float, nullable=True)  # 触发变动百分比
    trigger_time = Column(DateTime(timezone=True), nullable=True)  # 触发时间
    trigger_volume = Column(Float, nullable=True)  # 触发交易量
    condition_params = Column(JSON, nullable=True)  # 其他条件参数
    
    # 目标订单
    order_direction = Column(String(10), nullable=False)  # BUY/SELL
    order_quantity = Column(Float, nullable=False)  # 交易数量 (MWh)
    order_price_type = Column(String(20), default="MARKET")  # MARKET/LIMIT
    order_limit_price = Column(Float, nullable=True)  # 限价单价格
    
    # 状态
    status = Column(String(20), default=ConditionStatus.PENDING.value)
    is_enabled = Column(Boolean, default=True)
    
    # 有效期
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)  # 过期时间
    
    # 触发信息
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    triggered_price = Column(Float, nullable=True)  # 触发时的价格
    
    # 执行信息
    executed_at = Column(DateTime(timezone=True), nullable=True)
    executed_order_id = Column(String, nullable=True)  # 关联的实际订单ID
    execution_result = Column(JSON, nullable=True)  # 执行结果
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConditionalOrder(id={self.id}, type='{self.condition_type}', status='{self.status}')>"
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if self.valid_until is None:
            return False
        return datetime.now() > self.valid_until
    
    def can_trigger(self) -> bool:
        """检查是否可以触发"""
        return (
            self.status == ConditionStatus.PENDING.value 
            and self.is_enabled 
            and not self.is_expired()
        )


class TriggerLog(Base):
    """触发日志"""
    
    __tablename__ = "trigger_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    conditional_order_id = Column(Integer, ForeignKey("conditional_orders.id"), nullable=False)
    
    # 触发信息
    trigger_time = Column(DateTime(timezone=True), server_default=func.now())
    trigger_reason = Column(String(200), nullable=True)
    market_price = Column(Float, nullable=True)  # 触发时的市场价格
    market_data = Column(JSON, nullable=True)  # 触发时的市场数据快照
    
    # 执行结果
    success = Column(Boolean, default=False)
    order_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<TriggerLog(id={self.id}, order_id={self.conditional_order_id}, success={self.success})>"
