"""
PowerX 缓存服务
创建日期: 2026-01-07
作者: zhi.qu

业务层缓存封装
"""
from typing import Any, Optional, Dict, List, TypeVar, Generic, Callable
from datetime import datetime
import json
from functools import wraps
from loguru import logger

from app.core.redis_client import get_redis


T = TypeVar('T')


class CacheTTL:
    """缓存过期时间常量 (秒)"""
    REALTIME = 5          # 实时数据 5秒
    SHORT = 60            # 短期 1分钟
    MEDIUM = 300          # 中期 5分钟
    LONG = 1800           # 长期 30分钟
    SESSION = 3600        # 会话 1小时
    CONFIG = 86400        # 配置 1天


class CacheKey:
    """缓存键前缀"""
    MARKET_PRICE = "market:price"
    MARKET_STATS = "market:stats"
    USER_SESSION = "user:session"
    USER_PROFILE = "user:profile"
    ORDER_STATUS = "order:status"
    CONFIG = "config"
    AI_PREDICTION = "ai:prediction"
    REPORT = "report"
    
    @staticmethod
    def market_price(province: str) -> str:
        return f"{CacheKey.MARKET_PRICE}:{province}"
    
    @staticmethod
    def user_session(user_id: str) -> str:
        return f"{CacheKey.USER_SESSION}:{user_id}"
    
    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"{CacheKey.USER_PROFILE}:{user_id}"
    
    @staticmethod
    def order_status(order_id: str) -> str:
        return f"{CacheKey.ORDER_STATUS}:{order_id}"
    
    @staticmethod
    def ai_prediction(model: str, key: str) -> str:
        return f"{CacheKey.AI_PREDICTION}:{model}:{key}"


class CacheService:
    """缓存服务"""
    
    def __init__(self):
        self._local_cache: Dict[str, Any] = {}
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        try:
            redis = get_redis()
            return await redis.get(key)
        except Exception as e:
            logger.warning(f"缓存获取失败: {e}")
            return self._local_cache.get(key)
    
    async def get_json(self, key: str) -> Optional[Dict]:
        """获取 JSON 缓存"""
        data = await self.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set(self, key: str, value: str, ttl: int = CacheTTL.MEDIUM):
        """设置缓存"""
        try:
            redis = get_redis()
            await redis.set(key, value, ex=ttl)
        except Exception as e:
            logger.warning(f"缓存设置失败: {e}")
            self._local_cache[key] = value
    
    async def set_json(self, key: str, value: Any, ttl: int = CacheTTL.MEDIUM):
        """设置 JSON 缓存"""
        data = json.dumps(value, ensure_ascii=False, default=str)
        await self.set(key, data, ttl)
    
    async def delete(self, key: str):
        """删除缓存"""
        try:
            redis = get_redis()
            await redis.delete(key)
        except Exception as e:
            logger.warning(f"缓存删除失败: {e}")
        self._local_cache.pop(key, None)
    
    async def delete_pattern(self, pattern: str):
        """删除匹配的缓存"""
        try:
            redis = get_redis()
            keys = await redis.keys(pattern)
            for key in keys:
                await redis.delete(key)
        except Exception as e:
            logger.warning(f"缓存批量删除失败: {e}")
    
    async def exists(self, key: str) -> bool:
        """检查是否存在"""
        try:
            redis = get_redis()
            return await redis.exists(key)
        except Exception:
            return key in self._local_cache
    
    # 业务方法
    async def get_market_price(self, province: str) -> Optional[Dict]:
        """获取市场价格"""
        key = CacheKey.market_price(province)
        return await self.get_json(key)
    
    async def set_market_price(self, province: str, data: Dict):
        """设置市场价格"""
        key = CacheKey.market_price(province)
        await self.set_json(key, data, CacheTTL.REALTIME)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict]:
        """获取用户会话"""
        key = CacheKey.user_session(user_id)
        return await self.get_json(key)
    
    async def set_user_session(self, user_id: str, data: Dict):
        """设置用户会话"""
        key = CacheKey.user_session(user_id)
        await self.set_json(key, data, CacheTTL.SESSION)
    
    async def invalidate_user_session(self, user_id: str):
        """使用户会话失效"""
        key = CacheKey.user_session(user_id)
        await self.delete(key)
    
    async def get_order_status(self, order_id: str) -> Optional[str]:
        """获取订单状态"""
        key = CacheKey.order_status(order_id)
        return await self.get(key)
    
    async def set_order_status(self, order_id: str, status: str):
        """设置订单状态"""
        key = CacheKey.order_status(order_id)
        await self.set(key, status, CacheTTL.SHORT)
    
    async def get_config(self, config_key: str) -> Optional[Dict]:
        """获取配置"""
        key = f"{CacheKey.CONFIG}:{config_key}"
        return await self.get_json(key)
    
    async def set_config(self, config_key: str, data: Dict):
        """设置配置"""
        key = f"{CacheKey.CONFIG}:{config_key}"
        await self.set_json(key, data, CacheTTL.CONFIG)
    
    async def get_stats(self) -> Dict:
        """获取缓存统计"""
        try:
            redis = get_redis()
            keys = await redis.keys("*")
            return {
                "total_keys": len(keys),
                "is_redis": redis.is_redis,
                "local_cache_size": len(self._local_cache)
            }
        except Exception:
            return {
                "total_keys": 0,
                "is_redis": False,
                "local_cache_size": len(self._local_cache)
            }


# 缓存装饰器
def cached(key_prefix: str, ttl: int = CacheTTL.MEDIUM):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            key_parts = [key_prefix]
            key_parts.extend(str(arg) for arg in args[1:])  # 跳过 self
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # 尝试获取缓存
            cache = cache_service
            cached_data = await cache.get_json(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            if result is not None:
                await cache.set_json(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# 单例
cache_service = CacheService()


def get_cache_service() -> CacheService:
    """获取缓存服务"""
    return cache_service
