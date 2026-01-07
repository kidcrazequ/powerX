"""
PowerX 开放 API 服务
创建日期: 2026-01-07
作者: zhi.qu
"""
import uuid
import hashlib
import secrets
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from app.models.open_api import APIKey, APIUsageLog, APIKeyStatus


class OpenAPIService:
    """开放 API 服务"""
    
    # 可用权限
    AVAILABLE_PERMISSIONS = [
        "market.read",       # 读取市场数据
        "market.subscribe",  # 订阅实时数据
        "order.read",        # 读取订单
        "order.create",      # 创建订单
        "order.cancel",      # 取消订单
        "position.read",     # 读取持仓
        "account.read",      # 读取账户
        "report.read",       # 读取报表
    ]
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_api_key(
        self,
        user_id: str,
        name: str,
        description: str = None,
        permissions: List[str] = None,
        allowed_ips: List[str] = None,
        rate_limit: int = 1000,
        expires_days: int = 365
    ) -> Dict[str, str]:
        """创建 API 密钥"""
        key_id = f"KEY-{uuid.uuid4().hex[:12].upper()}"
        
        # 生成密钥
        api_key = f"pk_{secrets.token_urlsafe(32)}"
        api_secret = secrets.token_urlsafe(48)
        
        # 哈希存储 secret
        secret_hash = hashlib.sha256(api_secret.encode()).hexdigest()
        
        # 验证权限
        if permissions:
            permissions = [p for p in permissions if p in self.AVAILABLE_PERMISSIONS]
        else:
            permissions = ["market.read"]
        
        key = APIKey(
            key_id=key_id,
            user_id=user_id,
            name=name,
            description=description,
            api_key=api_key,
            api_secret=secret_hash,
            permissions=permissions,
            allowed_ips=allowed_ips,
            rate_limit=rate_limit,
            status=APIKeyStatus.ACTIVE.value,
            expires_at=datetime.now() + timedelta(days=expires_days)
        )
        
        self.db.add(key)
        await self.db.commit()
        await self.db.refresh(key)
        
        logger.info(f"创建 API 密钥: {key_id}")
        
        # 返回密钥（仅此一次）
        return {
            "key_id": key_id,
            "api_key": api_key,
            "api_secret": api_secret,  # 仅此一次显示
            "permissions": permissions,
            "expires_at": key.expires_at.isoformat()
        }
    
    async def verify_api_key(
        self,
        api_key: str,
        api_secret: str,
        request_ip: str = None
    ) -> Optional[APIKey]:
        """验证 API 密钥"""
        query = select(APIKey).where(
            APIKey.api_key == api_key,
            APIKey.status == APIKeyStatus.ACTIVE.value
        )
        result = await self.db.execute(query)
        key = result.scalars().first()
        
        if not key:
            return None
        
        # 验证 secret
        secret_hash = hashlib.sha256(api_secret.encode()).hexdigest()
        if key.api_secret != secret_hash:
            return None
        
        # 检查过期
        if key.expires_at and key.expires_at < datetime.now():
            key.status = APIKeyStatus.EXPIRED.value
            await self.db.commit()
            return None
        
        # 检查 IP
        if key.allowed_ips and request_ip:
            if request_ip not in key.allowed_ips:
                return None
        
        # 更新使用信息
        key.request_count = (key.request_count or 0) + 1
        key.last_used_at = datetime.now()
        await self.db.commit()
        
        return key
    
    async def check_permission(
        self,
        api_key: str,
        permission: str
    ) -> bool:
        """检查权限"""
        query = select(APIKey).where(APIKey.api_key == api_key)
        result = await self.db.execute(query)
        key = result.scalars().first()
        
        if not key or not key.permissions:
            return False
        
        return permission in key.permissions
    
    async def list_api_keys(self, user_id: str) -> List[APIKey]:
        """列出用户的 API 密钥"""
        query = select(APIKey).where(
            APIKey.user_id == user_id
        ).order_by(APIKey.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def revoke_api_key(self, key_id: str) -> bool:
        """吊销 API 密钥"""
        query = select(APIKey).where(APIKey.key_id == key_id)
        result = await self.db.execute(query)
        key = result.scalars().first()
        
        if not key:
            return False
        
        key.status = APIKeyStatus.REVOKED.value
        await self.db.commit()
        
        logger.info(f"API 密钥已吊销: {key_id}")
        return True
    
    async def log_usage(
        self,
        key_id: str,
        endpoint: str,
        method: str,
        request_ip: str,
        status_code: int,
        response_time_ms: int
    ):
        """记录使用日志"""
        log = APIUsageLog(
            key_id=key_id,
            endpoint=endpoint,
            method=method,
            request_ip=request_ip,
            status_code=status_code,
            response_time_ms=response_time_ms
        )
        
        self.db.add(log)
        await self.db.commit()
    
    async def get_usage_stats(
        self,
        key_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """获取使用统计"""
        start_date = datetime.now() - timedelta(days=days)
        
        query = select(APIUsageLog).where(
            and_(
                APIUsageLog.key_id == key_id,
                APIUsageLog.created_at >= start_date
            )
        )
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        if not logs:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "success_rate": 0
            }
        
        total = len(logs)
        success = sum(1 for log in logs if 200 <= log.status_code < 300)
        avg_time = sum(log.response_time_ms or 0 for log in logs) / total
        
        return {
            "total_requests": total,
            "avg_response_time": round(avg_time, 2),
            "success_rate": round(success / total * 100, 2)
        }


def get_open_api_service(db: AsyncSession) -> OpenAPIService:
    """获取开放 API 服务"""
    return OpenAPIService(db)
