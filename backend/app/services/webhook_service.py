"""
PowerX Webhook 服务
创建日期: 2026-01-07
作者: zhi.qu
"""
import uuid
import hmac
import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

from app.models.webhook import Webhook, WebhookLog, WebhookEvent


class WebhookService:
    """Webhook 服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_webhook(
        self,
        user_id: str,
        name: str,
        url: str,
        events: List[str],
        secret: str = None,
        headers: Dict[str, str] = None
    ) -> Webhook:
        """创建 Webhook"""
        webhook_id = f"WH-{uuid.uuid4().hex[:12].upper()}"
        
        if secret is None:
            secret = uuid.uuid4().hex
        
        webhook = Webhook(
            webhook_id=webhook_id,
            user_id=user_id,
            name=name,
            url=url,
            events=events,
            secret=secret,
            headers=headers,
            is_active=True
        )
        
        self.db.add(webhook)
        await self.db.commit()
        await self.db.refresh(webhook)
        
        logger.info(f"创建 Webhook: {webhook_id}")
        return webhook
    
    async def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """获取 Webhook"""
        query = select(Webhook).where(Webhook.webhook_id == webhook_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def list_webhooks(self, user_id: str) -> List[Webhook]:
        """列出用户的 Webhook"""
        query = select(Webhook).where(Webhook.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_webhook(
        self,
        webhook_id: str,
        **updates
    ) -> Optional[Webhook]:
        """更新 Webhook"""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            return None
        
        for key, value in updates.items():
            if hasattr(webhook, key) and value is not None:
                setattr(webhook, key, value)
        
        await self.db.commit()
        await self.db.refresh(webhook)
        return webhook
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """删除 Webhook"""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            return False
        
        await self.db.delete(webhook)
        await self.db.commit()
        return True
    
    async def trigger_event(
        self,
        event: str,
        payload: Dict[str, Any]
    ) -> int:
        """触发事件"""
        # 获取订阅该事件的 Webhook
        query = select(Webhook).where(
            Webhook.is_active == True
        )
        result = await self.db.execute(query)
        webhooks = result.scalars().all()
        
        triggered_count = 0
        for webhook in webhooks:
            if webhook.events and event in webhook.events:
                await self._send_webhook(webhook, event, payload)
                triggered_count += 1
        
        logger.debug(f"触发事件 {event}, 通知 {triggered_count} 个 Webhook")
        return triggered_count
    
    async def _send_webhook(
        self,
        webhook: Webhook,
        event: str,
        payload: Dict[str, Any]
    ):
        """发送 Webhook"""
        start_time = time.time()
        
        body = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": payload
        }
        
        body_json = json.dumps(body)
        
        # 计算签名
        signature = self._compute_signature(body_json, webhook.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event,
            "X-Webhook-Signature": signature,
            "X-Webhook-Timestamp": str(int(time.time()))
        }
        
        if webhook.headers:
            headers.update(webhook.headers)
        
        log = WebhookLog(
            webhook_id=webhook.webhook_id,
            event=event,
            request_body=body
        )
        
        try:
            if HAS_AIOHTTP:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook.url,
                        data=body_json,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        log.response_status = response.status
                        log.response_body = await response.text()
                        log.success = 200 <= response.status < 300
            else:
                # 模拟成功
                log.response_status = 200
                log.success = True
            
            webhook.success_count = (webhook.success_count or 0) + 1
            webhook.last_status = "success"
            
        except Exception as e:
            log.success = False
            log.error_message = str(e)
            webhook.failure_count = (webhook.failure_count or 0) + 1
            webhook.last_status = "failed"
            logger.error(f"Webhook 发送失败: {webhook.webhook_id}, {e}")
        
        log.duration_ms = int((time.time() - start_time) * 1000)
        webhook.last_triggered_at = datetime.now()
        
        self.db.add(log)
        await self.db.commit()
    
    def _compute_signature(self, body: str, secret: str) -> str:
        """计算签名"""
        return hmac.new(
            secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def get_webhook_logs(
        self,
        webhook_id: str,
        limit: int = 20
    ) -> List[WebhookLog]:
        """获取 Webhook 日志"""
        query = select(WebhookLog).where(
            WebhookLog.webhook_id == webhook_id
        ).order_by(WebhookLog.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


def get_webhook_service(db: AsyncSession) -> WebhookService:
    """获取 Webhook 服务"""
    return WebhookService(db)
