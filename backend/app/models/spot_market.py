"""
PowerX 现货市场模型

创建日期: 2026-01-07
作者: zhi.qu

定义现货电价和价格历史的数据模型
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class SpotPrice(Base):
    """
    现货电价模型
    
    表示日前和实时现货电价
    """
    __tablename__ = "spot_prices"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 省份和节点
    province = Column(String(20), nullable=False, index=True, comment="省份")
    node_name = Column(String(50), nullable=True, comment="节点名称（节点电价省份）")
    
    # 交易日期和时段
    trading_date = Column(Date, nullable=False, index=True, comment="交易日期")
    hour = Column(Integer, nullable=False, comment="时段（0-23）")
    
    # 电价
    day_ahead_price = Column(Float, nullable=True, comment="日前电价（元/MWh）")
    realtime_price = Column(Float, nullable=True, comment="实时电价（元/MWh）")
    
    # 成交量
    volume_mwh = Column(Float, default=0, comment="成交电量（MWh）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_spot_price_province_date_hour', 'province', 'trading_date', 'hour'),
    )
    
    # 关联关系
    price_history = relationship("PriceHistory", back_populates="spot_price")
    
    def __repr__(self):
        return f"<SpotPrice(province='{self.province}', date={self.trading_date}, hour={self.hour})>"


class PriceHistory(Base):
    """
    价格历史模型
    
    记录价格的历史变化（用于分析价格波动）
    """
    __tablename__ = "price_history"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联现货电价
    spot_id = Column(Integer, nullable=False, index=True)
    
    # 价格记录
    price = Column(Float, nullable=False, comment="价格（元/MWh）")
    price_type = Column(String(20), nullable=False, comment="价格类型（day_ahead/realtime）")
    volume_mwh = Column(Float, default=0, comment="成交电量（MWh）")
    
    # 时间戳
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, comment="记录时间")
    
    # 关联关系
    spot_price = relationship("SpotPrice", back_populates="price_history", foreign_keys=[spot_id], 
                              primaryjoin="PriceHistory.spot_id == SpotPrice.id")
    
    def __repr__(self):
        return f"<PriceHistory(spot_id={self.spot_id}, price={self.price}, type='{self.price_type}')>"


class LoadData(Base):
    """
    负荷数据模型
    
    记录各省份的负荷数据
    """
    __tablename__ = "load_data"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 省份
    province = Column(String(20), nullable=False, index=True, comment="省份")
    
    # 日期和时段
    trading_date = Column(Date, nullable=False, index=True, comment="日期")
    hour = Column(Integer, nullable=False, comment="时段（0-23）")
    
    # 负荷数据
    actual_load_mw = Column(Float, nullable=True, comment="实际负荷（MW）")
    forecast_load_mw = Column(Float, nullable=True, comment="预测负荷（MW）")
    
    # 新能源出力
    wind_power_mw = Column(Float, nullable=True, comment="风电出力（MW）")
    solar_power_mw = Column(Float, nullable=True, comment="光伏出力（MW）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_load_data_province_date_hour', 'province', 'trading_date', 'hour'),
    )
    
    def __repr__(self):
        return f"<LoadData(province='{self.province}', date={self.trading_date}, hour={self.hour})>"
