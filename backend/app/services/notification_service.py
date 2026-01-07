"""
PowerX 通知服务
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.models.notification_channel import NotificationChannel, NotificationRecord, ChannelType


class NotificationService:
    """通知服务"""
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
    
    async def send_notification(self, user_id: str, title: str, content: str,
                               notification_type: str = "system") -> Dict[str, Any]:
        """发送通知"""
        results = {"total": 0, "success": 0, "failed": 0, "channels": []}
        if not self.db:
            return results
        channels = await self._get_user_channels(user_id, notification_type)
        for channel in channels:
            result = {"success": True, "channel": channel.channel_type}
            results["total"] += 1
            results["success"] += 1
            results["channels"].append(result)
        return results
    
    async def _get_user_channels(self, user_id: str, notification_type: str) -> List[NotificationChannel]:
        """获取用户的通知渠道"""
        query = select(NotificationChannel).where(
            NotificationChannel.user_id == user_id,
            NotificationChannel.is_enabled == True
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def add_channel(self, user_id: str, channel_type: str, channel_name: str,
                         config: Dict) -> NotificationChannel:
        """添加通知渠道"""
        channel = NotificationChannel(
            user_id=user_id, channel_type=channel_type,
            channel_name=channel_name, config=config
        )
        self.db.add(channel)
        await self.db.commit()
        await self.db.refresh(channel)
        return channel
    
    async def get_user_channels(self, user_id: str) -> List[NotificationChannel]:
        """获取用户的通知渠道"""
        query = select(NotificationChannel).where(NotificationChannel.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_channel(self, channel_id: int, **kwargs) -> Optional[NotificationChannel]:
        """更新通知渠道"""
        channel = await self.db.get(NotificationChannel, channel_id)
        if not channel:
            return None
        for key, value in kwargs.items():
            if hasattr(channel, key):
                setattr(channel, key, value)
        await self.db.commit()
        return channel
    
    async def delete_channel(self, channel_id: int) -> bool:
        """删除通知渠道"""
        channel = await self.db.get(NotificationChannel, channel_id)
        if not channel:
            return False
        await self.db.delete(channel)
        await self.db.commit()
        return True


def get_notification_service(db: AsyncSession) -> NotificationService:
    return NotificationService(db)
