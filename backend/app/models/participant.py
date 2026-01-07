"""
PowerX 市场参与主体模型

创建日期: 2026-01-07
作者: zhi.qu

定义市场参与主体（发电企业、售电公司、大用户等）的数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.constants import ParticipantType, UserLevel, Province


class MarketParticipant(Base):
    """
    市场参与主体模型
    
    表示电力市场中的各类参与者
    """
    __tablename__ = "market_participants"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    
    # 市场主体信息
    name = Column(String(100), nullable=False, comment="企业/机构名称")
    participant_type = Column(
        SQLEnum(ParticipantType),
        nullable=False,
        default=ParticipantType.RETAILER,
        comment="参与主体类型"
    )
    province = Column(String(20), nullable=False, default="广东", comment="所属省份")
    
    # 资质信息
    license_no = Column(String(50), nullable=True, comment="营业执照号/售电公司编号")
    credit_rating = Column(String(10), nullable=True, comment="信用等级")
    registered_capital = Column(Integer, nullable=True, comment="注册资本（万元）")
    
    # 交易员水平（用于 AI 辅助策略差异化）
    level = Column(
        SQLEnum(UserLevel),
        nullable=False,
        default=UserLevel.BEGINNER,
        comment="交易员水平"
    )
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 关联关系
    orders = relationship("TradingOrder", back_populates="participant")
    positions = relationship("Position", back_populates="participant")
    buy_contracts = relationship("Contract", foreign_keys="Contract.buyer_id", back_populates="buyer")
    sell_contracts = relationship("Contract", foreign_keys="Contract.seller_id", back_populates="seller")
    
    def __repr__(self):
        return f"<MarketParticipant(id={self.id}, name='{self.name}', type={self.participant_type})>"
