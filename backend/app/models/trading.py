"""
PowerX 交易订单模型

创建日期: 2026-01-07
作者: zhi.qu

定义交易订单和持仓的数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.constants import MarketType, TradingPeriod, OrderDirection, OrderStatus


class TradingOrder(Base):
    """
    交易订单模型
    
    表示现货和中长期交易的订单
    """
    __tablename__ = "trading_orders"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联市场主体
    participant_id = Column(Integer, ForeignKey("market_participants.id"), nullable=False, index=True)
    
    # 订单基本信息
    order_no = Column(String(50), unique=True, index=True, nullable=False, comment="订单编号")
    market_type = Column(
        SQLEnum(MarketType),
        nullable=False,
        comment="市场类型"
    )
    trading_period = Column(
        SQLEnum(TradingPeriod),
        nullable=False,
        comment="交易时段"
    )
    direction = Column(
        SQLEnum(OrderDirection),
        nullable=False,
        comment="交易方向"
    )
    
    # 价格和数量
    price = Column(Float, nullable=False, comment="报价（元/MWh）")
    quantity_mwh = Column(Float, nullable=False, comment="申报电量（MWh）")
    filled_quantity_mwh = Column(Float, default=0, comment="已成交电量（MWh）")
    avg_filled_price = Column(Float, nullable=True, comment="成交均价（元/MWh）")
    
    # 省份和节点
    province = Column(String(20), nullable=False, default="广东", comment="省份")
    node_name = Column(String(50), nullable=True, comment="节点名称（节点电价省份）")
    
    # 交易日期和时段
    trading_date = Column(Date, nullable=False, comment="交易日期")
    hour_start = Column(Integer, nullable=True, comment="开始时段（小时）")
    hour_end = Column(Integer, nullable=True, comment="结束时段（小时）")
    
    # 订单状态
    status = Column(
        SQLEnum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        comment="订单状态"
    )
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    filled_at = Column(DateTime, nullable=True, comment="成交时间")
    
    # 关联关系
    participant = relationship("MarketParticipant", back_populates="orders")
    
    def __repr__(self):
        return f"<TradingOrder(id={self.id}, order_no='{self.order_no}', status={self.status})>"


class Position(Base):
    """
    持仓模型
    
    表示市场主体在各市场的持仓情况
    """
    __tablename__ = "positions"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联市场主体
    participant_id = Column(Integer, ForeignKey("market_participants.id"), nullable=False, index=True)
    
    # 持仓信息
    province = Column(String(20), nullable=False, default="广东", comment="省份")
    market_type = Column(
        SQLEnum(MarketType),
        nullable=False,
        comment="市场类型"
    )
    
    # 持仓量
    net_position_mwh = Column(Float, default=0, comment="净持仓量（MWh），正为多头，负为空头")
    buy_quantity_mwh = Column(Float, default=0, comment="买入总量（MWh）")
    sell_quantity_mwh = Column(Float, default=0, comment="卖出总量（MWh）")
    
    # 成本和盈亏
    avg_cost = Column(Float, default=0, comment="平均成本（元/MWh）")
    unrealized_pnl = Column(Float, default=0, comment="未实现盈亏（元）")
    realized_pnl = Column(Float, default=0, comment="已实现盈亏（元）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    participant = relationship("MarketParticipant", back_populates="positions")
    
    def __repr__(self):
        return f"<Position(id={self.id}, participant_id={self.participant_id}, net={self.net_position_mwh})>"
