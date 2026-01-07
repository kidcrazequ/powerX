"""
PowerX 交易规则数据模型

创建日期: 2026-01-07
作者: zhi.qu

定义交易规则引擎相关的数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class RuleStatus(str, enum.Enum):
    """规则状态"""
    ACTIVE = "ACTIVE"       # 激活
    INACTIVE = "INACTIVE"   # 未激活
    PAUSED = "PAUSED"       # 暂停
    DELETED = "DELETED"     # 已删除


class ActionType(str, enum.Enum):
    """动作类型"""
    PLACE_ORDER = "PLACE_ORDER"           # 下单
    SEND_ALERT = "SEND_ALERT"             # 发送预警
    CANCEL_ORDER = "CANCEL_ORDER"         # 取消订单
    ADJUST_POSITION = "ADJUST_POSITION"   # 调整仓位
    EXECUTE_STRATEGY = "EXECUTE_STRATEGY" # 执行策略


class TradingRule(Base):
    """交易规则"""
    
    __tablename__ = "trading_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 规则配置
    priority = Column(Integer, default=0)  # 优先级，数字越大优先级越高
    status = Column(String(20), default=RuleStatus.INACTIVE.value)
    
    # 条件表达式 (JSON格式)
    # 例如: {"operator": "AND", "conditions": [{"field": "price", "op": ">", "value": 500}]}
    condition_expression = Column(JSON, nullable=False)
    
    # 适用范围
    provinces = Column(JSON, nullable=True)  # 适用省份列表，null表示所有
    market_types = Column(JSON, nullable=True)  # 适用市场类型
    
    # 动作配置
    action_type = Column(String(50), nullable=False)
    action_params = Column(JSON, nullable=True)  # 动作参数
    
    # 执行限制
    max_executions_per_day = Column(Integer, default=10)  # 每日最大执行次数
    min_interval_seconds = Column(Integer, default=60)  # 最小执行间隔(秒)
    max_total_executions = Column(Integer, nullable=True)  # 总最大执行次数
    
    # 统计
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    today_execution_count = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联
    executions = relationship("RuleExecution", back_populates="rule", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TradingRule(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def can_execute(self) -> bool:
        """检查规则是否可以执行"""
        if self.status != RuleStatus.ACTIVE.value:
            return False
        
        # 检查每日执行次数
        if self.today_execution_count >= self.max_executions_per_day:
            return False
        
        # 检查总执行次数
        if self.max_total_executions and self.execution_count >= self.max_total_executions:
            return False
        
        # 检查执行间隔
        if self.last_executed_at:
            elapsed = (datetime.now() - self.last_executed_at).total_seconds()
            if elapsed < self.min_interval_seconds:
                return False
        
        return True


class RuleExecution(Base):
    """规则执行记录"""
    
    __tablename__ = "rule_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("trading_rules.id"), nullable=False)
    
    # 执行信息
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    trigger_data = Column(JSON, nullable=True)  # 触发时的数据快照
    
    # 条件评估
    condition_results = Column(JSON, nullable=True)  # 条件评估结果
    
    # 动作执行
    action_executed = Column(String(50), nullable=True)
    action_result = Column(JSON, nullable=True)
    
    # 结果
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # 关联的订单(如果有)
    order_id = Column(String, nullable=True)
    
    # 关联
    rule = relationship("TradingRule", back_populates="executions")
    
    def __repr__(self):
        return f"<RuleExecution(id={self.id}, rule_id={self.rule_id}, success={self.success})>"
