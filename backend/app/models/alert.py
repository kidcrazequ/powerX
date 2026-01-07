"""
PowerX 预警模型

创建日期: 2026-01-07
作者: zhi.qu

预警规则和预警记录
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AlertType(str, Enum):
    """预警类型"""
    PRICE_HIGH = "PRICE_HIGH"           # 价格过高
    PRICE_LOW = "PRICE_LOW"             # 价格过低
    PRICE_CHANGE = "PRICE_CHANGE"       # 价格波动
    VOLUME_ABNORMAL = "VOLUME_ABNORMAL" # 成交量异常
    POSITION_RISK = "POSITION_RISK"     # 持仓风险
    CONTRACT_EXPIRE = "CONTRACT_EXPIRE" # 合同到期
    SETTLEMENT_DUE = "SETTLEMENT_DUE"   # 结算到期
    MARKET_CLOSE = "MARKET_CLOSE"       # 市场关闭
    SYSTEM_ERROR = "SYSTEM_ERROR"       # 系统错误
    CUSTOM = "CUSTOM"                   # 自定义预警


class AlertLevel(str, Enum):
    """预警级别"""
    INFO = "INFO"           # 信息
    WARNING = "WARNING"     # 警告
    DANGER = "DANGER"       # 危险
    CRITICAL = "CRITICAL"   # 紧急


class AlertStatus(str, Enum):
    """预警状态"""
    PENDING = "PENDING"       # 待处理
    ACKNOWLEDGED = "ACKNOWLEDGED"  # 已确认
    RESOLVED = "RESOLVED"     # 已解决
    IGNORED = "IGNORED"       # 已忽略


class AlertRule(Base):
    """
    预警规则表
    
    定义触发预警的条件
    """
    __tablename__ = "alert_rules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 规则基本信息
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="规则名称")
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="规则描述")
    alert_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="预警类型")
    level: Mapped[str] = mapped_column(String(16), default=AlertLevel.WARNING.value, comment="预警级别")
    
    # 规则条件
    province: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, comment="适用省份")
    condition_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="条件类型")
    condition_value: Mapped[float] = mapped_column(Float, nullable=False, comment="条件阈值")
    condition_operator: Mapped[str] = mapped_column(String(16), default=">=", comment="比较运算符")
    condition_extra: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True, comment="额外条件")
    
    # 通知配置
    notify_methods: Mapped[Optional[List]] = mapped_column(JSON, default=["websocket"], comment="通知方式")
    notify_users: Mapped[Optional[List]] = mapped_column(JSON, nullable=True, comment="通知用户")
    
    # 规则状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="创建用户ID")
    
    # 执行信息
    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后触发时间")
    trigger_count: Mapped[int] = mapped_column(Integer, default=0, comment="触发次数")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self) -> str:
        return f"<AlertRule {self.id}: {self.name}>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "alert_type": self.alert_type,
            "level": self.level,
            "province": self.province,
            "condition_type": self.condition_type,
            "condition_value": self.condition_value,
            "condition_operator": self.condition_operator,
            "is_active": self.is_active,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AlertRecord(Base):
    """
    预警记录表
    
    记录所有触发的预警
    """
    __tablename__ = "alert_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 关联规则
    rule_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="规则ID")
    rule_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="规则名称")
    
    # 预警信息
    alert_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="预警类型")
    level: Mapped[str] = mapped_column(String(16), nullable=False, comment="预警级别")
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="预警标题")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="预警内容")
    
    # 上下文信息
    province: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, comment="省份")
    target_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, comment="目标类型")
    target_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="目标ID")
    context: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True, comment="上下文数据")
    
    # 当前值与阈值
    current_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="当前值")
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="阈值")
    
    # 状态
    status: Mapped[str] = mapped_column(String(16), default=AlertStatus.PENDING.value, comment="状态")
    
    # 处理信息
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="关联用户ID")
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="确认人")
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="确认时间")
    resolved_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="解决人")
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="解决时间")
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="解决备注")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    def __repr__(self) -> str:
        return f"<AlertRecord {self.id}: {self.title}>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "alert_type": self.alert_type,
            "level": self.level,
            "title": self.title,
            "message": self.message,
            "province": self.province,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "status": self.status,
            "user_id": self.user_id,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
