"""
PowerX 数据库配置

创建日期: 2026-01-07
作者: zhi.qu

数据库连接和会话管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.core.config import settings


# 判断是否使用 SQLite
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# 创建异步数据库引擎
# SQLite 不支持 pool_size 和 max_overflow 参数
if is_sqlite:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """声明式基类"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话
    
    Yields:
        AsyncSession: 异步数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
