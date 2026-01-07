"""
PowerX 定时报表模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Time
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class ScheduleFrequency(str, Enum):
    """调度频率"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ReportSchedule(Base):
    """报表调度配置"""
    
    __tablename__ = "report_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String(50), unique=True, index=True)
    
    # 基本信息
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 报表模板
    template_id = Column(Integer, index=True)
    
    # 调度配置
    frequency = Column(String(20), default=ScheduleFrequency.DAILY.value)
    schedule_time = Column(Time)  # 执行时间
    schedule_day = Column(Integer)  # 周几(1-7)或几号(1-31)
    cron_expression = Column(String(100))  # 自定义cron表达式
    
    # 报表参数
    parameters = Column(JSON)
    
    # 发送配置
    recipients = Column(JSON)  # 接收人列表
    send_email = Column(Boolean, default=True)
    send_wechat = Column(Boolean, default=False)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 统计
    last_run_at = Column(DateTime(timezone=True))
    last_run_status = Column(String(20))
    run_count = Column(Integer, default=0)
    
    created_by = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ScheduledReportLog(Base):
    """调度执行日志"""
    
    __tablename__ = "scheduled_report_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String(50), index=True)
    
    # 执行信息
    run_id = Column(String(50), unique=True, index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # 结果
    status = Column(String(20))  # success, failed, partial
    report_file = Column(String(255))  # 生成的报表文件路径
    
    # 发送结果
    recipients_count = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
