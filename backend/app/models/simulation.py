"""
PowerX 交易模拟模型

创建日期: 2026-01-07
作者: zhi.qu

定义回测记录和模拟交易相关的数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class SimulationStatus(str, enum.Enum):
    """模拟/回测状态"""
    PENDING = "PENDING"       # 等待执行
    RUNNING = "RUNNING"       # 执行中
    COMPLETED = "COMPLETED"   # 已完成
    FAILED = "FAILED"         # 失败
    CANCELLED = "CANCELLED"   # 已取消


class SimulationSession(Base):
    """回测/模拟交易会话"""
    
    __tablename__ = "simulation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 模拟类型
    simulation_type = Column(String(50), nullable=False)  # BACKTEST, PAPER_TRADING
    
    # 策略配置
    strategy_name = Column(String(100), nullable=False)
    strategy_params = Column(JSON, nullable=True)  # 策略参数
    
    # 时间范围 (回测用)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # 初始资金
    initial_capital = Column(Float, default=1000000.0)
    
    # 状态
    status = Column(String(20), default=SimulationStatus.PENDING.value)
    progress = Column(Float, default=0.0)  # 0-100
    
    # 结果统计
    final_capital = Column(Float, nullable=True)
    total_return = Column(Float, nullable=True)  # 总收益率
    annual_return = Column(Float, nullable=True)  # 年化收益率
    max_drawdown = Column(Float, nullable=True)  # 最大回撤
    sharpe_ratio = Column(Float, nullable=True)  # 夏普比率
    win_rate = Column(Float, nullable=True)  # 胜率
    total_trades = Column(Integer, nullable=True)  # 总交易次数
    
    # 详细结果
    result_data = Column(JSON, nullable=True)  # 完整结果数据
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关联的交易记录
    trades = relationship("SimulationTrade", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SimulationSession(id={self.id}, name='{self.name}', status='{self.status}')>"


class SimulationTrade(Base):
    """模拟交易记录"""
    
    __tablename__ = "simulation_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("simulation_sessions.id"), nullable=False)
    
    # 交易信息
    trade_time = Column(DateTime(timezone=True), nullable=False)
    direction = Column(String(10), nullable=False)  # BUY, SELL
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)  # price * quantity
    
    # 费用
    commission = Column(Float, default=0.0)
    
    # 盈亏 (平仓时计算)
    profit = Column(Float, nullable=True)
    profit_rate = Column(Float, nullable=True)
    
    # 交易原因/信号
    signal = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # 关联
    session = relationship("SimulationSession", back_populates="trades")
    
    def __repr__(self):
        return f"<SimulationTrade(id={self.id}, direction='{self.direction}', amount={self.amount})>"
