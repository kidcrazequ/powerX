"""
PowerX 自定义指标模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.sql import func

from app.core.database import Base


class CustomIndicator(Base):
    """自定义指标"""
    
    __tablename__ = "custom_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String(50), unique=True, index=True)
    
    user_id = Column(String(50), index=True)
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 计算公式
    formula = Column(Text, nullable=False)  # 公式表达式
    variables = Column(JSON)  # 变量定义
    
    # 数据源
    data_source = Column(String(50))  # price, volume, position
    
    # 单位
    unit = Column(String(20))
    
    # 显示配置
    display_config = Column(JSON)  # 颜色、图表类型等
    
    # 状态
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IndicatorValue(Base):
    """指标计算值"""
    
    __tablename__ = "indicator_values"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String(50), index=True)
    
    timestamp = Column(DateTime(timezone=True), index=True)
    value = Column(Float)
    
    context = Column(JSON)  # 计算上下文
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
