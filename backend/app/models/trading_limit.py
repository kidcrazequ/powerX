"""
PowerX 交易限额数据模型

创建日期: 2026-01-07
作者: zhi.qu

定义交易限额和违规记录相关的数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class LimitType(str, enum.Enum):
    """限额类型"""
    DAILY_AMOUNT = "DAILY_AMOUNT"       # 每日交易金额
    DAILY_QUANTITY = "DAILY_QUANTITY"   # 每日交易数量
    SINGLE_AMOUNT = "SINGLE_AMOUNT"     # 单笔交易金额
    SINGLE_QUANTITY = "SINGLE_QUANTITY" # 单笔交易数量
    POSITION = "POSITION"               # 持仓限额


class TradingLimit(Base):
    """交易限额配置"""
    
    __tablename__ = "trading_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)  # null 表示全局限额
    
    # 限额配置
    limit_type = Column(String(50), nullable=False)
    limit_value = Column(Float, nullable=False)  # 限额值
    
    # 适用范围
    province = Column(String(50), nullable=True)  # null 表示所有省份
    market_type = Column(String(50), nullable=True)  # null 表示所有市场
    direction = Column(String(10), nullable=True)  # BUY/SELL/null(两者)
    
    # 状态
    is_enabled = Column(Boolean, default=True)
    
    # 元数据
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<TradingLimit(id={self.id}, type='{self.limit_type}', value={self.limit_value})>"


class LimitViolation(Base):
    """限额违规记录"""
    
    __tablename__ = "limit_violations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    limit_id = Column(Integer, ForeignKey("trading_limits.id"), nullable=False)
    
    # 违规详情
    violation_time = Column(DateTime(timezone=True), server_default=func.now())
    attempted_value = Column(Float, nullable=False)  # 尝试的值
    limit_value = Column(Float, nullable=False)  # 当时的限额值
    current_usage = Column(Float, nullable=True)  # 当前已使用额度
    
    # 交易信息
    order_data = Column(JSON, nullable=True)  # 尝试的订单数据
    
    # 处理状态
    is_resolved = Column(Boolean, default=False)
    resolution_note = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<LimitViolation(id={self.id}, user='{self.user_id}', limit_id={self.limit_id})>"


class DailyUsage(Base):
    """每日使用量跟踪"""
    
    __tablename__ = "daily_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)  # YYYY-MM-DD
    
    # 使用统计
    total_buy_quantity = Column(Float, default=0)  # 买入总量
    total_sell_quantity = Column(Float, default=0)  # 卖出总量
    total_buy_amount = Column(Float, default=0)  # 买入总金额
    total_sell_amount = Column(Float, default=0)  # 卖出总金额
    trade_count = Column(Integer, default=0)  # 交易次数
    
    # 按省份统计
    by_province = Column(JSON, default=dict)
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DailyUsage(user='{self.user_id}', date='{self.date}')>"
