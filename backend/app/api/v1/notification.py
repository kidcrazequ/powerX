"""
PowerX 通知 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.notification_service import NotificationService
from app.models.notification_channel import ChannelType
from app.schemas.response import APIResponse

router = APIRouter()


class ChannelCreate(BaseModel):
    channel_type: str
    channel_name: str
    config: Dict = Field(default_factory=dict)


@router.get("/channels", response_model=APIResponse[List[Dict[str, Any]]])
async def get_channels(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """获取我的通知渠道"""
    service = NotificationService(db)
    channels = await service.get_user_channels(current_user.id)
    return APIResponse.success_response([
        {"id": c.id, "channel_type": c.channel_type, "channel_name": c.channel_name, "is_enabled": c.is_enabled}
        for c in channels
    ])


@router.post("/channels", response_model=APIResponse[Dict[str, Any]])
async def create_channel(request: ChannelCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """添加通知渠道"""
    service = NotificationService(db)
    channel = await service.add_channel(current_user.id, request.channel_type, request.channel_name, request.config)
    return APIResponse.success_response({"id": channel.id}, message="添加成功")


@router.delete("/channels/{channel_id}", response_model=APIResponse[bool])
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """删除通知渠道"""
    service = NotificationService(db)
    success = await service.delete_channel(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="渠道不存在")
    return APIResponse.success_response(True, message="已删除")


@router.get("/types", response_model=APIResponse[List[Dict[str, str]]])
async def get_channel_types(current_user = Depends(get_current_user)):
    """获取支持的渠道类型"""
    return APIResponse.success_response([
        {"value": ChannelType.EMAIL.value, "label": "电子邮件"},
        {"value": ChannelType.WECHAT.value, "label": "企业微信"},
        {"value": ChannelType.DINGTALK.value, "label": "钉钉"},
    ])
