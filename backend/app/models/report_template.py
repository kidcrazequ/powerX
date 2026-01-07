"""
PowerX 报表模板模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class ReportType(str, Enum):
    """报表类型"""
    TRADING = "trading"      # 交易报表
    SETTLEMENT = "settlement"  # 结算报表
    RISK = "risk"            # 风险报表
    MARKET = "market"        # 市场报表
    CUSTOM = "custom"        # 自定义报表


class ChartType(str, Enum):
    """图表类型"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    TABLE = "table"
    STAT = "stat"


class ReportTemplate(Base):
    """报表模板"""
    
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), default=ReportType.CUSTOM.value)
    
    # 创建者
    created_by = Column(String, nullable=False)
    
    # 模板配置 (JSON格式)
    layout = Column(JSON, default=list)  # 布局配置
    data_sources = Column(JSON, default=list)  # 数据源配置
    filters = Column(JSON, default=list)  # 筛选条件
    
    # 状态
    is_public = Column(Boolean, default=False)  # 是否公开
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ReportWidget(Base):
    """报表组件"""
    
    __tablename__ = "report_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, index=True, nullable=False)
    
    widget_type = Column(String(50), default=ChartType.LINE.value)
    title = Column(String(100), nullable=False)
    
    # 位置和大小
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=6)
    height = Column(Integer, default=4)
    
    # 数据配置
    data_source = Column(String(100))  # 数据源名称
    query_config = Column(JSON, default=dict)  # 查询配置
    chart_config = Column(JSON, default=dict)  # 图表配置
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GeneratedReport(Base):
    """生成的报表"""
    
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, index=True)
    name = Column(String(200), nullable=False)
    
    # 生成信息
    generated_by = Column(String, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 报表参数
    parameters = Column(JSON, default=dict)
    
    # 报表数据 (缓存)
    data = Column(JSON)
    
    # 导出信息
    export_format = Column(String(20))  # pdf, excel, html
    file_path = Column(String(500))
