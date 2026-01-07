"""
PowerX API 依赖项

创建日期: 2026-01-07
作者: zhi.qu

FastAPI 依赖注入
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db as db_session
from app.core.security import verify_token


# Bearer 令牌提取器
security = HTTPBearer(auto_error=False)


class MockUser:
    """模拟用户对象（用于演示）"""
    def __init__(self, id: int = 1, username: str = "demo", name: str = "演示用户"):
        self.id = id
        self.username = username
        self.name = name
        self.email = f"{username}@example.com"
        self.is_active = True
        self.role = "trader"


async def get_db() -> AsyncSession:
    """
    获取数据库会话
    
    Yields:
        AsyncSession: 数据库会话
    """
    async for session in db_session():
        yield session


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> MockUser:
    """
    获取当前用户
    
    Args:
        credentials: HTTP Bearer 凭证
        
    Returns:
        当前用户
        
    Raises:
        HTTPException: 认证失败
    """
    # 演示模式：如果没有提供令牌，返回模拟用户
    if not credentials:
        return MockUser()
    
    token = credentials.credentials
    
    # 验证令牌
    user_id = verify_token(token, token_type="access")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 返回用户（实际应从数据库查询）
    return MockUser(id=int(user_id))


async def get_current_active_user(
    current_user: MockUser = Depends(get_current_user)
) -> MockUser:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        活跃用户
        
    Raises:
        HTTPException: 用户被禁用
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    return current_user
