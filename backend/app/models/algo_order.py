"""
PowerX 算法订单模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class AlgoType(str, Enum):
    """算法类型"""
    TWAP = "twap"       # 时间加权平均价格
    VWAP = "vwap"       # 成交量加权平均价格
    ICEBERG = "iceberg" # 冰山订单
    POV = "pov"         # 成交量百分比
    SNIPER = "sniper"   # 狙击手


class AlgoOrderStatus(str, Enum):
    """算法订单状态"""
    CREATED = "created"     # 已创建
    RUNNING = "running"     # 运行中
    PAUSED = "paused"       # 已暂停
    COMPLETED = "completed" # 已完成
    CANCELLED = "cancelled" # 已取消
    FAILED = "failed"       # 失败


class AlgoOrder(Base):
    """算法订单"""
    
    __tablename__ = "algo_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    algo_id = Column(String(50), unique=True, index=True, nullable=False)
    
    user_id = Column(String, index=True, nullable=False)
    
    # 算法类型和参数
    algo_type = Column(String(20), nullable=False)
    algo_params = Column(JSON)  # 算法参数
    
    # 交易信息
    province = Column(String(20), default="guangdong")
    market_type = Column(String(20), default="spot")
    order_type = Column(String(10))  # buy, sell
    
    # 目标
    target_quantity = Column(Float, nullable=False)  # 目标数量
    target_price = Column(Float)  # 目标价格 (限价)
    price_limit_upper = Column(Float)  # 价格上限
    price_limit_lower = Column(Float)  # 价格下限
    
    # 执行时间窗口
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    
    # 执行状态
    status = Column(String(20), default=AlgoOrderStatus.CREATED.value)
    
    # 执行结果
    filled_quantity = Column(Float, default=0)
    avg_price = Column(Float)
    slices_total = Column(Integer, default=0)  # 总切片数
    slices_filled = Column(Integer, default=0)  # 已成交切片数
    
    # 执行日志
    execution_log = Column(JSON)
    
    # 错误信息
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))


class AlgoSlice(Base):
    """算法订单切片"""
    
    __tablename__ = "algo_slices"
    
    id = Column(Integer, primary_key=True, index=True)
    algo_order_id = Column(Integer, index=True, nullable=False)
    slice_id = Column(String(50), unique=True, index=True)
    
    # 切片信息
    sequence = Column(Integer)  # 序号
    scheduled_time = Column(DateTime(timezone=True))  # 计划执行时间
    
    quantity = Column(Float)
    price = Column(Float)
    
    # 执行结果
    status = Column(String(20), default="pending")
    filled_quantity = Column(Float, default=0)
    filled_price = Column(Float)
    
    executed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
