"""
PowerX 合同模型

创建日期: 2026-01-07
作者: zhi.qu

定义电力交易合同的数据模型
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.constants import ContractType


class ContractStatus:
    """合同状态常量"""
    DRAFT = "DRAFT"           # 草稿
    PENDING = "PENDING"       # 待确认
    ACTIVE = "ACTIVE"         # 生效中
    COMPLETED = "COMPLETED"   # 已完成
    TERMINATED = "TERMINATED" # 已终止


class Contract(Base):
    """
    电力交易合同模型
    
    表示年度长协、月度双边、月度竞价等各类合同
    """
    __tablename__ = "contracts"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 合同编号
    contract_no = Column(String(50), unique=True, index=True, nullable=False, comment="合同编号")
    
    # 合同类型
    contract_type = Column(
        SQLEnum(ContractType),
        nullable=False,
        comment="合同类型"
    )
    
    # 交易双方
    buyer_id = Column(Integer, ForeignKey("market_participants.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("market_participants.id"), nullable=False, index=True)
    
    # 省份
    province = Column(String(20), nullable=False, default="广东", comment="省份")
    
    # 合同条款
    total_quantity_mwh = Column(Float, nullable=False, comment="合同总电量（MWh）")
    executed_quantity_mwh = Column(Float, default=0, comment="已执行电量（MWh）")
    price = Column(Float, nullable=False, comment="合同价格（元/MWh）")
    
    # 合同期限
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    
    # 分解曲线（JSON 格式存储）
    decomposition_curve = Column(JSON, nullable=True, comment="电量分解曲线")
    
    # 合同状态
    status = Column(String(20), default=ContractStatus.DRAFT, comment="合同状态")
    
    # 备注
    remarks = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    signed_at = Column(DateTime, nullable=True, comment="签订时间")
    
    # 关联关系
    buyer = relationship("MarketParticipant", foreign_keys=[buyer_id], back_populates="buy_contracts")
    seller = relationship("MarketParticipant", foreign_keys=[seller_id], back_populates="sell_contracts")
    
    @property
    def remaining_quantity_mwh(self) -> float:
        """剩余电量"""
        return self.total_quantity_mwh - self.executed_quantity_mwh
    
    @property
    def execution_rate(self) -> float:
        """执行率"""
        if self.total_quantity_mwh == 0:
            return 0
        return self.executed_quantity_mwh / self.total_quantity_mwh
    
    def __repr__(self):
        return f"<Contract(id={self.id}, no='{self.contract_no}', type={self.contract_type})>"


class ContractExecution(Base):
    """
    合同执行记录模型
    
    记录合同的日度执行情况
    """
    __tablename__ = "contract_executions"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联合同
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    
    # 执行日期
    execution_date = Column(Date, nullable=False, comment="执行日期")
    
    # 执行电量
    planned_quantity_mwh = Column(Float, nullable=False, comment="计划电量（MWh）")
    actual_quantity_mwh = Column(Float, default=0, comment="实际电量（MWh）")
    deviation_quantity_mwh = Column(Float, default=0, comment="偏差电量（MWh）")
    
    # 执行价格
    execution_price = Column(Float, nullable=True, comment="执行价格（元/MWh）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    def __repr__(self):
        return f"<ContractExecution(contract_id={self.contract_id}, date={self.execution_date})>"
