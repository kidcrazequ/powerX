"""
PowerX 预测记录模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class PredictionRecord(Base):
    """预测记录"""
    
    __tablename__ = "prediction_records"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(50), unique=True, index=True)
    
    # 预测类型
    prediction_type = Column(String(30), index=True)  # price, load, trend
    
    # 预测目标
    province = Column(String(20), index=True)
    market_type = Column(String(20))
    target_time = Column(DateTime(timezone=True), index=True)  # 预测目标时间
    
    # 预测结果
    predicted_value = Column(Float)
    predicted_range_low = Column(Float)  # 预测区间下限
    predicted_range_high = Column(Float)  # 预测区间上限
    confidence = Column(Float)  # 置信度
    
    # 模型信息
    model_name = Column(String(50))
    model_version = Column(String(20))
    
    # 输入特征
    input_features = Column(JSON)
    
    # 实际结果
    actual_value = Column(Float)
    
    # 对账结果
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime(timezone=True))
    
    # 误差分析
    error = Column(Float)
    error_percentage = Column(Float)
    within_range = Column(Boolean)  # 是否在预测区间内
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReconciliationReport(Base):
    """对账报告"""
    
    __tablename__ = "reconciliation_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, index=True)
    
    # 报告周期
    period_type = Column(String(20))  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    # 统计信息
    prediction_type = Column(String(30))
    province = Column(String(20))
    
    total_predictions = Column(Integer)
    reconciled_count = Column(Integer)
    
    # 准确性指标
    accuracy = Column(Float)  # 方向准确率
    mae = Column(Float)       # 平均绝对误差
    mape = Column(Float)      # 平均绝对百分比误差
    rmse = Column(Float)      # 均方根误差
    
    # 区间预测准确性
    range_hit_rate = Column(Float)  # 落入预测区间的比例
    
    # 趋势分析
    trend_accuracy = Column(Float)  # 趋势预测准确率
    
    # 详细数据
    details = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
