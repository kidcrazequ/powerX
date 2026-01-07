"""
PowerX 系统配置

创建日期: 2026-01-07
作者: zhi.qu

应用配置管理
"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "PowerX"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "智能电力交易系统"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库 (使用 SQLite 作为默认值，方便本地开发)
    DATABASE_URL: str = "sqlite+aiosqlite:///./powerx.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str = "powerx-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # DeepSeek API
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # 电力市场
    DEFAULT_PROVINCE: str = "广东"
    SUPPORTED_PROVINCES: List[str] = ["广东", "浙江", "山东", "山西", "甘肃"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略未定义的环境变量


def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
