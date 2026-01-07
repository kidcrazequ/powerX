"""
PowerX Webhook API
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.webhook_service import get_webhook_service

router = APIRouter(prefix="/webhooks", tags=["Webhook"])


class CreateWebhookRequest(BaseModel):
    """创建 Webhook 请求"""
    name: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    headers: Optional[dict] = None


class UpdateWebhookRequest(BaseModel):
    """更新 Webhook 请求"""
    name: Optional[str] = None
    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    """Webhook 响应"""
    webhook_id: str
    name: str
    url: str
    events: List[str]
    is_active: bool
    success_count: int
    failure_count: int


class WebhookLogResponse(BaseModel):
    """Webhook 日志响应"""
    event: str
    response_status: Optional[int]
    success: bool
    duration_ms: Optional[int]


@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    request: CreateWebhookRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建 Webhook"""
    service = get_webhook_service(db)
    
    webhook = await service.create_webhook(
        user_id="user-001",
        name=request.name,
        url=request.url,
        events=request.events,
        secret=request.secret,
        headers=request.headers
    )
    
    return WebhookResponse(
        webhook_id=webhook.webhook_id,
        name=webhook.name,
        url=webhook.url,
        events=webhook.events or [],
        is_active=webhook.is_active,
        success_count=webhook.success_count or 0,
        failure_count=webhook.failure_count or 0
    )


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    db: AsyncSession = Depends(get_db)
):
    """列出 Webhook"""
    service = get_webhook_service(db)
    webhooks = await service.list_webhooks(user_id="user-001")
    
    return [
        WebhookResponse(
            webhook_id=w.webhook_id,
            name=w.name,
            url=w.url,
            events=w.events or [],
            is_active=w.is_active,
            success_count=w.success_count or 0,
            failure_count=w.failure_count or 0
        )
        for w in webhooks
    ]


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取 Webhook"""
    service = get_webhook_service(db)
    webhook = await service.get_webhook(webhook_id)
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook 不存在")
    
    return WebhookResponse(
        webhook_id=webhook.webhook_id,
        name=webhook.name,
        url=webhook.url,
        events=webhook.events or [],
        is_active=webhook.is_active,
        success_count=webhook.success_count or 0,
        failure_count=webhook.failure_count or 0
    )


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    request: UpdateWebhookRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新 Webhook"""
    service = get_webhook_service(db)
    
    webhook = await service.update_webhook(
        webhook_id=webhook_id,
        **request.model_dump(exclude_none=True)
    )
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook 不存在")
    
    return WebhookResponse(
        webhook_id=webhook.webhook_id,
        name=webhook.name,
        url=webhook.url,
        events=webhook.events or [],
        is_active=webhook.is_active,
        success_count=webhook.success_count or 0,
        failure_count=webhook.failure_count or 0
    )


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除 Webhook"""
    service = get_webhook_service(db)
    success = await service.delete_webhook(webhook_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Webhook 不存在")
    
    return {"success": True, "message": "Webhook 已删除"}


@router.get("/{webhook_id}/logs", response_model=List[WebhookLogResponse])
async def get_webhook_logs(
    webhook_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取 Webhook 日志"""
    service = get_webhook_service(db)
    logs = await service.get_webhook_logs(webhook_id, limit)
    
    return [
        WebhookLogResponse(
            event=log.event,
            response_status=log.response_status,
            success=log.success,
            duration_ms=log.duration_ms
        )
        for log in logs
    ]


@router.post("/test")
async def test_webhook(
    url: str,
    db: AsyncSession = Depends(get_db)
):
    """测试 Webhook"""
    service = get_webhook_service(db)
    
    # 触发测试事件
    await service.trigger_event(
        event="test.event",
        payload={
            "message": "This is a test webhook"
        }
    )
    
    return {"success": True, "message": "测试事件已发送"}
