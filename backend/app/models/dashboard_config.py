"""
PowerX 仪表盘配置模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class DashboardLayout(Base):
    """用户仪表盘布局配置"""
    
    __tablename__ = "dashboard_layouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String(100), default="默认布局")
    
    # 布局配置 (JSON格式存储每个组件的位置和大小)
    layout = Column(JSON, default=list)
    
    # 是否为默认布局
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WidgetConfig(Base):
    """仪表盘组件配置"""
    
    __tablename__ = "widget_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    widget_type = Column(String(50), nullable=False)  # price_chart, order_list, etc
    widget_name = Column(String(100), nullable=False)
    
    # 组件配置
    config = Column(JSON, default=dict)
    
    # 位置信息
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)
    
    is_visible = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
