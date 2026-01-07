"""
PowerX 自动学习记录模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class LearningRecord(Base):
    """学习记录"""
    
    __tablename__ = "learning_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联信息
    model_name = Column(String(50), index=True)
    strategy_id = Column(String(50), index=True)
    
    # 学习类型
    learning_type = Column(String(30))  # feedback, optimization, evaluation
    
    # 输入数据
    input_data = Column(JSON)
    
    # 预测值
    predicted_value = Column(Float)
    predicted_direction = Column(String(10))  # up, down, stable
    
    # 实际值
    actual_value = Column(Float)
    actual_direction = Column(String(10))
    
    # 评估指标
    error = Column(Float)  # 预测误差
    error_percentage = Column(Float)  # 误差百分比
    direction_correct = Column(Boolean)  # 方向是否正确
    
    # 反馈
    feedback_score = Column(Float)  # 用户反馈评分 (1-5)
    feedback_comment = Column(Text)
    
    # 时间
    prediction_time = Column(DateTime(timezone=True))
    actual_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StrategyOptimization(Base):
    """策略优化记录"""
    
    __tablename__ = "strategy_optimizations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    strategy_id = Column(String(50), index=True)
    version = Column(Integer, default=1)
    
    # 优化前参数
    params_before = Column(JSON)
    
    # 优化后参数
    params_after = Column(JSON)
    
    # 优化原因
    optimization_reason = Column(Text)
    
    # 效果评估
    performance_before = Column(JSON)  # 优化前性能指标
    performance_after = Column(JSON)   # 优化后性能指标
    improvement = Column(Float)        # 改进百分比
    
    # 是否采纳
    is_adopted = Column(Boolean, default=False)
    adopted_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelPerformance(Base):
    """模型性能记录"""
    
    __tablename__ = "model_performances"
    
    id = Column(Integer, primary_key=True, index=True)
    
    model_name = Column(String(50), index=True)
    period = Column(String(20))  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), index=True)
    period_end = Column(DateTime(timezone=True))
    
    # 统计指标
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    accuracy = Column(Float)
    
    # 误差指标
    mae = Column(Float)  # 平均绝对误差
    mse = Column(Float)  # 均方误差
    rmse = Column(Float)  # 均方根误差
    mape = Column(Float)  # 平均绝对百分比误差
    
    # 方向准确率
    direction_accuracy = Column(Float)
    
    # 收益相关
    total_profit = Column(Float)
    win_rate = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
