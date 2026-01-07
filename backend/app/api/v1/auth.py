"""
PowerX 认证 API

创建日期: 2026-01-07
作者: zhi.qu

用户认证相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token
)
from app.core.config import settings
from app.api.deps import get_current_user, MockUser

router = APIRouter()


# ============ 请求/响应模型 ============

class Token(BaseModel):
    """令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class UserCreate(BaseModel):
    """用户注册请求"""
    username: str
    password: str
    email: str
    name: str
    participant_type: str = "RETAILER"
    province: str = "广东"


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    name: str
    role: str
    is_active: bool


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


# ============ 模拟用户数据 ============

MOCK_USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password_hash": get_password_hash("admin123"),
        "email": "admin@powerx.com",
        "name": "系统管理员",
        "role": "admin",
        "is_active": True
    },
    "demo": {
        "id": 2,
        "username": "demo",
        "password_hash": get_password_hash("demo123"),
        "email": "demo@powerx.com",
        "name": "演示用户",
        "role": "trader",
        "is_active": True
    }
}


# ============ API 端点 ============

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """
    用户登录
    
    使用用户名和密码登录，获取访问令牌
    """
    user = MOCK_USERS.get(request.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建令牌
    access_token = create_access_token(subject=user["id"])
    refresh_token = create_refresh_token(subject=user["id"])
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 兼容登录
    
    用于 Swagger UI 的 OAuth2 密码流程
    """
    user = MOCK_USERS.get(form_data.username)
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(subject=user["id"])
    refresh_token = create_refresh_token(subject=user["id"])
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: TokenRefresh):
    """
    刷新令牌
    
    使用刷新令牌获取新的访问令牌
    """
    user_id = verify_token(request.refresh_token, token_type="refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    # 创建新令牌
    access_token = create_access_token(subject=user_id)
    refresh_token = create_refresh_token(subject=user_id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: MockUser = Depends(get_current_user)
):
    """
    获取当前用户信息
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active
    )


@router.post("/register", response_model=UserResponse)
async def register(request: UserCreate):
    """
    用户注册
    
    注册新用户（演示模式）
    """
    if request.username in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户（实际应保存到数据库）
    new_user = {
        "id": len(MOCK_USERS) + 1,
        "username": request.username,
        "password_hash": get_password_hash(request.password),
        "email": request.email,
        "name": request.name,
        "role": "trader",
        "is_active": True
    }
    
    MOCK_USERS[request.username] = new_user
    
    return UserResponse(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        name=new_user["name"],
        role=new_user["role"],
        is_active=new_user["is_active"]
    )


@router.post("/logout")
async def logout(current_user: MockUser = Depends(get_current_user)):
    """
    用户登出
    
    使当前令牌失效（实际应加入黑名单）
    """
    return {"message": "登出成功"}
