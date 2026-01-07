"""
PowerX 期权合约模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class OptionType(str, Enum):
    """期权类型"""
    CALL = "call"  # 看涨期权
    PUT = "put"    # 看跌期权


class OptionStyle(str, Enum):
    """期权风格"""
    EUROPEAN = "european"  # 欧式期权
    AMERICAN = "american"  # 美式期权


class OptionOrderStatus(str, Enum):
    """期权订单状态"""
    PENDING = "pending"
    OPEN = "open"
    EXERCISED = "exercised"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class OptionContract(Base):
    """期权合约"""
    
    __tablename__ = "option_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(String(50), unique=True, index=True)
    
    # 合约信息
    name = Column(String(100))
    underlying = Column(String(50))  # 标的物(如: 广东电力)
    
    # 期权类型
    option_type = Column(String(10))  # call/put
    option_style = Column(String(10))  # european/american
    
    # 执行价格
    strike_price = Column(Float, nullable=False)
    
    # 合约规模
    contract_size = Column(Float, default=1)  # MWh
    
    # 到期日
    expiration_date = Column(DateTime(timezone=True), nullable=False)
    
    # 权利金
    premium = Column(Float)  # 每MWh权利金
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OptionOrder(Base):
    """期权订单"""
    
    __tablename__ = "option_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True)
    
    user_id = Column(String(50), index=True)
    contract_id = Column(String(50), index=True)
    
    # 交易方向
    side = Column(String(10))  # buy/sell
    
    # 开平仓
    position_effect = Column(String(10))  # open/close
    
    # 数量
    quantity = Column(Float, nullable=False)
    filled_quantity = Column(Float, default=0)
    
    # 价格
    price = Column(Float)  # 权利金报价
    total_premium = Column(Float)  # 总权利金
    
    # 状态
    status = Column(String(20), default=OptionOrderStatus.PENDING.value)
    
    # 行权信息
    exercise_date = Column(DateTime(timezone=True))
    settlement_price = Column(Float)
    profit_loss = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class OptionPosition(Base):
    """期权持仓"""
    
    __tablename__ = "option_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(String(50), index=True)
    contract_id = Column(String(50), index=True)
    
    # 持仓方向
    side = Column(String(10))  # long/short
    
    # 持仓数量
    quantity = Column(Float, nullable=False)
    
    # 平均成本
    avg_price = Column(Float)
    
    # 市值
    market_value = Column(Float)
    
    # 盈亏
    unrealized_pnl = Column(Float, default=0)
    realized_pnl = Column(Float, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
