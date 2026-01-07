"""
PowerX 核心配置模块

创建日期: 2026-01-07
作者: zhi.qu
"""

from app.core.config import settings
from app.core.database import get_db, engine, Base

__all__ = ["settings", "get_db", "engine", "Base"]
