"""
PowerX 开放 API 管理接口
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.open_api_service import get_open_api_service, OpenAPIService

router = APIRouter(prefix="/open-api", tags=["开放 API"])


class CreateAPIKeyRequest(BaseModel):
    """创建 API 密钥请求"""
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    allowed_ips: Optional[List[str]] = None
    rate_limit: int = 1000
    expires_days: int = 365


class APIKeyResponse(BaseModel):
    """API 密钥响应"""
    key_id: str
    name: str
    permissions: List[str]
    status: str
    request_count: int
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime


class APIKeyCreatedResponse(BaseModel):
    """新建密钥响应"""
    key_id: str
    api_key: str
    api_secret: str
    permissions: List[str]
    expires_at: str


@router.get("/permissions")
async def list_permissions():
    """获取可用权限列表"""
    return {
        "permissions": OpenAPIService.AVAILABLE_PERMISSIONS
    }


@router.post("/keys", response_model=APIKeyCreatedResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建 API 密钥"""
    service = get_open_api_service(db)
    
    result = await service.create_api_key(
        user_id="user-001",
        name=request.name,
        description=request.description,
        permissions=request.permissions,
        allowed_ips=request.allowed_ips,
        rate_limit=request.rate_limit,
        expires_days=request.expires_days
    )
    
    return APIKeyCreatedResponse(**result)


@router.get("/keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db)
):
    """列出 API 密钥"""
    service = get_open_api_service(db)
    keys = await service.list_api_keys(user_id="user-001")
    
    return [
        APIKeyResponse(
            key_id=k.key_id,
            name=k.name,
            permissions=k.permissions or [],
            status=k.status,
            request_count=k.request_count or 0,
            last_used_at=k.last_used_at,
            expires_at=k.expires_at,
            created_at=k.created_at
        )
        for k in keys
    ]


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db)
):
    """吊销 API 密钥"""
    service = get_open_api_service(db)
    success = await service.revoke_api_key(key_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="密钥不存在")
    
    return {"success": True, "message": "密钥已吊销"}


@router.get("/keys/{key_id}/stats")
async def get_key_stats(
    key_id: str,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """获取密钥使用统计"""
    service = get_open_api_service(db)
    stats = await service.get_usage_stats(key_id, days)
    
    return stats


# 公开 API 端点示例
@router.get("/v1/market/prices")
async def get_market_prices():
    """获取市场价格（公开 API）"""
    # 这里应该验证 API 密钥
    return {
        "prices": [
            {"province": "广东", "price": 450.5, "time": datetime.now().isoformat()},
            {"province": "江苏", "price": 420.3, "time": datetime.now().isoformat()},
            {"province": "浙江", "price": 435.8, "time": datetime.now().isoformat()}
        ]
    }


@router.get("/v1/market/summary")
async def get_market_summary():
    """获取市场摘要（公开 API）"""
    return {
        "total_volume": 125000,
        "avg_price": 428.5,
        "high_price": 480.0,
        "low_price": 380.0,
        "updated_at": datetime.now().isoformat()
    }
