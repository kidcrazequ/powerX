"""
PowerX 操作日志模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class OperationLog(Base):
    """操作日志 (用于回滚)"""
    
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(String(50), unique=True, index=True)
    
    # 操作信息
    operation_type = Column(String(50), index=True)  # create, update, delete
    entity_type = Column(String(50), index=True)  # order, contract, config
    entity_id = Column(String(100), index=True)
    
    # 操作者
    user_id = Column(String(50), index=True)
    
    # 操作前后数据
    data_before = Column(JSON)
    data_after = Column(JSON)
    
    # 变更描述
    description = Column(Text)
    
    # 回滚状态
    is_rollbackable = Column(Boolean, default=True)
    is_rolled_back = Column(Boolean, default=False)
    rolled_back_at = Column(DateTime(timezone=True))
    rolled_back_by = Column(String(50))
    
    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RollbackHistory(Base):
    """回滚历史"""
    
    __tablename__ = "rollback_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    operation_id = Column(String(50), index=True)
    
    # 回滚操作者
    user_id = Column(String(50))
    
    # 回滚结果
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
