"""
PowerX 交易日历模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class TradingCalendar(Base):
    """交易日历"""
    
    __tablename__ = "trading_calendars"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 日期信息
    date = Column(Date, unique=True, index=True, nullable=False)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    day = Column(Integer)
    weekday = Column(Integer)  # 0=周一, 6=周日
    
    # 交易状态
    is_trading_day = Column(Boolean, default=True)
    
    # 节假日信息
    is_holiday = Column(Boolean, default=False)
    holiday_name = Column(String(50))
    
    # 特殊日期
    is_special_day = Column(Boolean, default=False)
    special_rules = Column(JSON)  # 特殊规则
    
    # 交易时段
    morning_start = Column(Time)
    morning_end = Column(Time)
    afternoon_start = Column(Time)
    afternoon_end = Column(Time)
    
    # 备注
    notes = Column(Text)


class TradingSession(Base):
    """交易时段配置"""
    
    __tablename__ = "trading_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    province = Column(String(20), index=True)
    market_type = Column(String(20))  # spot, mid_long
    
    name = Column(String(50))  # 时段名称
    
    # 时间配置
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # 适用的星期 (JSON数组 [0,1,2,3,4] 表示周一到周五)
    weekdays = Column(JSON)
    
    # 是否启用
    is_active = Column(Boolean, default=True)
    
    # 规则
    order_types_allowed = Column(JSON)  # 允许的订单类型
    price_limit_rule = Column(String(50))  # 涨跌停规则
    
    created_at = Column(String(50), default=lambda: datetime.now().isoformat())


class Holiday(Base):
    """节假日配置"""
    
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(50), nullable=False)
    
    # 日期范围
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # 节假日类型
    holiday_type = Column(String(20))  # national, weekend_swap, special
    
    # 是否调休
    is_workday_swap = Column(Boolean, default=False)
    swap_date = Column(Date)  # 调休日期
    
    # 适用范围
    applies_to = Column(JSON)  # 适用的省份列表，空表示全国
    
    created_at = Column(String(50), default=lambda: datetime.now().isoformat())
