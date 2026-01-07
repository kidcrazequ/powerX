"""
PowerX 工作区模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class Workspace(Base):
    """用户工作区"""
    
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String(50), unique=True, index=True)
    
    user_id = Column(String(50), index=True, nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 工作区类型
    workspace_type = Column(String(30))  # trader, analyst, admin
    
    # 布局配置
    layout = Column(JSON)  # 页面布局
    widgets = Column(JSON)  # 组件配置
    
    # 快捷方式
    shortcuts = Column(JSON)  # 常用功能快捷方式
    
    # 主题
    theme = Column(String(20), default="dark")
    
    # 是否默认
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True))
