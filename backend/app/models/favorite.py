"""
PowerX 收藏夹模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class Favorite(Base):
    """用户收藏"""
    
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(String(50), index=True, nullable=False)
    
    # 收藏类型
    item_type = Column(String(30), index=True)  # contract, page, indicator, report
    item_id = Column(String(100), index=True)
    
    # 显示信息
    title = Column(String(200))
    description = Column(Text)
    icon = Column(String(50))
    
    # 元数据
    metadata = Column(JSON)
    
    # 排序
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FavoriteFolder(Base):
    """收藏夹文件夹"""
    
    __tablename__ = "favorite_folders"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(String(50), index=True, nullable=False)
    
    name = Column(String(100), nullable=False)
    icon = Column(String(50))
    color = Column(String(20))
    
    parent_id = Column(Integer)  # 父文件夹ID
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
