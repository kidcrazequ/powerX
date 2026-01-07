"""
PowerX 结算模型

创建日期: 2026-01-07
作者: zhi.qu

定义电力交易结算的数据模型
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey

from app.core.database import Base


class Settlement(Base):
    """
    结算记录模型
    
    记录市场主体的结算信息
    """
    __tablename__ = "settlements"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联市场主体
    participant_id = Column(Integer, ForeignKey("market_participants.id"), nullable=False, index=True)
    
    # 结算周期
    settlement_date = Column(Date, nullable=False, index=True, comment="结算日期")
    province = Column(String(20), nullable=False, comment="省份")
    market_type = Column(String(20), nullable=False, comment="市场类型")
    
    # 电量
    buy_quantity_mwh = Column(Float, default=0, comment="买入电量（MWh）")
    sell_quantity_mwh = Column(Float, default=0, comment="卖出电量（MWh）")
    net_quantity_mwh = Column(Float, default=0, comment="净电量（MWh）")
    
    # 金额
    buy_amount = Column(Float, default=0, comment="买入金额（元）")
    sell_amount = Column(Float, default=0, comment="卖出金额（元）")
    net_amount = Column(Float, default=0, comment="净结算金额（元）")
    
    # 均价
    avg_buy_price = Column(Float, nullable=True, comment="买入均价（元/MWh）")
    avg_sell_price = Column(Float, nullable=True, comment="卖出均价（元/MWh）")
    
    # 结算状态
    status = Column(String(20), default="PENDING", comment="结算状态")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    settled_at = Column(DateTime, nullable=True, comment="结算确认时间")
    
    def __repr__(self):
        return f"<Settlement(participant_id={self.participant_id}, date={self.settlement_date})>"


class DeviationSettlement(Base):
    """
    偏差结算模型
    
    记录合同执行偏差的结算信息
    """
    __tablename__ = "deviation_settlements"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联市场主体
    participant_id = Column(Integer, ForeignKey("market_participants.id"), nullable=False, index=True)
    
    # 关联合同
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True, index=True)
    
    # 结算日期
    settlement_date = Column(Date, nullable=False, index=True, comment="结算日期")
    province = Column(String(20), nullable=False, comment="省份")
    
    # 电量偏差
    contract_quantity_mwh = Column(Float, default=0, comment="合同电量（MWh）")
    actual_quantity_mwh = Column(Float, default=0, comment="实际电量（MWh）")
    deviation_quantity_mwh = Column(Float, default=0, comment="偏差电量（MWh）")
    deviation_rate = Column(Float, default=0, comment="偏差率")
    
    # 偏差结算
    deviation_price = Column(Float, default=0, comment="偏差结算价格（元/MWh）")
    deviation_amount = Column(Float, default=0, comment="偏差结算金额（元）")
    
    # 是否免考核
    is_exempt = Column(String(10), default="NO", comment="是否免考核")
    exempt_reason = Column(String(200), nullable=True, comment="免考核原因")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    def __repr__(self):
        return f"<DeviationSettlement(participant_id={self.participant_id}, date={self.settlement_date})>"
