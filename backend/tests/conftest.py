"""
PowerX 测试配置

创建日期: 2026-01-07
作者: zhi.qu

Pytest 配置和测试夹具
"""

import pytest
import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base


# 测试数据库 URL（使用 SQLite 内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建数据库会话"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "测试售电公司",
        "participant_type": "RETAILER",
        "province": "广东"
    }


@pytest.fixture
def sample_order_data():
    """示例订单数据"""
    return {
        "market_type": "DAY_AHEAD",
        "trading_period": "DAILY",
        "direction": "BUY",
        "price": 485.0,
        "quantity_mwh": 100.0,
        "province": "广东"
    }
