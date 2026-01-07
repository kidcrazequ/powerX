"""
PowerX Redis 客户端
创建日期: 2026-01-07
作者: zhi.qu

Redis 连接池和缓存管理
"""
import asyncio
from typing import Any, Optional, Dict, List, Union
from datetime import timedelta
import json
from loguru import logger

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logger.warning("redis 未安装，使用内存缓存模式")


class MemoryCache:
    """内存缓存 (开发/测试用)"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        async with self._lock:
            if key in self._expiry:
                import time
                if time.time() > self._expiry[key]:
                    del self._cache[key]
                    del self._expiry[key]
                    return None
            return self._cache.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        """设置缓存"""
        async with self._lock:
            self._cache[key] = value
            if ex:
                import time
                self._expiry[key] = time.time() + ex
    
    async def delete(self, key: str):
        """删除缓存"""
        async with self._lock:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """检查是否存在"""
        return await self.get(key) is not None
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取键列表"""
        async with self._lock:
            if pattern == "*":
                return list(self._cache.keys())
            import fnmatch
            return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Hash 获取"""
        data = await self.get(name)
        if data:
            d = json.loads(data)
            return d.get(key)
        return None
    
    async def hset(self, name: str, key: str, value: str):
        """Hash 设置"""
        async with self._lock:
            data = self._cache.get(name)
            if data:
                d = json.loads(data)
            else:
                d = {}
            d[key] = value
            self._cache[name] = json.dumps(d)
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """Hash 获取全部"""
        data = await self.get(name)
        if data:
            return json.loads(data)
        return {}
    
    async def incr(self, key: str) -> int:
        """自增"""
        async with self._lock:
            val = int(self._cache.get(key, 0)) + 1
            self._cache[key] = str(val)
            return val
    
    async def expire(self, key: str, seconds: int):
        """设置过期时间"""
        async with self._lock:
            import time
            self._expiry[key] = time.time() + seconds
    
    async def ttl(self, key: str) -> int:
        """获取剩余时间"""
        async with self._lock:
            if key in self._expiry:
                import time
                remaining = int(self._expiry[key] - time.time())
                return max(0, remaining)
            return -1
    
    async def close(self):
        """关闭"""
        pass


class RedisClient:
    """Redis 客户端"""
    
    _instance: Optional["RedisClient"] = None
    
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self.url = url
        self._pool: Optional[aioredis.Redis] = None
        self._memory_fallback = MemoryCache()
        self._use_redis = HAS_REDIS
    
    @classmethod
    def get_instance(cls, url: str = None) -> "RedisClient":
        """获取单例"""
        if cls._instance is None:
            cls._instance = cls(url or "redis://localhost:6379/0")
        return cls._instance
    
    async def connect(self):
        """建立连接"""
        if not self._use_redis:
            logger.info("使用内存缓存模式")
            return
        
        try:
            self._pool = aioredis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            await self._pool.ping()
            logger.info("Redis 连接成功")
        except Exception as e:
            logger.warning(f"Redis 连接失败，使用内存缓存: {e}")
            self._use_redis = False
    
    async def disconnect(self):
        """断开连接"""
        if self._pool:
            await self._pool.close()
        logger.info("Redis 连接已关闭")
    
    @property
    def client(self):
        """获取客户端"""
        if self._use_redis and self._pool:
            return self._pool
        return self._memory_fallback
    
    async def get(self, key: str) -> Optional[str]:
        """获取"""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        """设置"""
        await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        """删除"""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """是否存在"""
        if self._use_redis:
            return await self.client.exists(key) > 0
        return await self.client.exists(key)
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取键列表"""
        return await self.client.keys(pattern)
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Hash 获取"""
        return await self.client.hget(name, key)
    
    async def hset(self, name: str, key: str, value: str):
        """Hash 设置"""
        await self.client.hset(name, key, value)
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """Hash 获取全部"""
        return await self.client.hgetall(name)
    
    async def incr(self, key: str) -> int:
        """自增"""
        return await self.client.incr(key)
    
    async def expire(self, key: str, seconds: int):
        """设置过期时间"""
        await self.client.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """获取剩余时间"""
        return await self.client.ttl(key)
    
    @property
    def is_redis(self) -> bool:
        """是否使用 Redis"""
        return self._use_redis


# 便捷函数
redis_client: Optional[RedisClient] = None


async def init_redis(url: str = None):
    """初始化 Redis"""
    global redis_client
    redis_client = RedisClient.get_instance(url)
    await redis_client.connect()
    return redis_client


async def close_redis():
    """关闭 Redis"""
    global redis_client
    if redis_client:
        await redis_client.disconnect()
        redis_client = None


def get_redis() -> RedisClient:
    """获取 Redis 客户端"""
    if redis_client is None:
        raise RuntimeError("Redis 未初始化")
    return redis_client
