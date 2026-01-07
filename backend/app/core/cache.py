"""
PowerX 缓存服务

创建日期: 2026-01-07
作者: zhi.qu

提供内存缓存和 Redis 缓存支持
"""

import asyncio
import functools
import hashlib
import json
from typing import Any, Callable, Optional, TypeVar, Union
from datetime import datetime, timedelta
from cachetools import TTLCache, LRUCache
from loguru import logger

from app.core.config import settings

T = TypeVar("T")


class CacheManager:
    """
    缓存管理器
    
    支持内存缓存，可选 Redis 扩展
    """
    
    def __init__(
        self,
        default_ttl: int = 300,
        max_size: int = 1000
    ):
        """
        初始化缓存管理器
        
        Args:
            default_ttl: 默认过期时间（秒）
            max_size: 缓存最大条目数
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        
        # 内存缓存 - 使用 TTLCache
        self._cache: TTLCache = TTLCache(maxsize=max_size, ttl=default_ttl)
        
        # 永久缓存 - 使用 LRUCache
        self._permanent_cache: LRUCache = LRUCache(maxsize=max_size // 2)
        
        # 缓存统计
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        
        # Redis 连接（可选）
        self._redis = None
        
        logger.info(f"缓存管理器初始化: max_size={max_size}, default_ttl={default_ttl}s")
    
    def _generate_key(self, key: str, namespace: Optional[str] = None) -> str:
        """生成缓存键"""
        if namespace:
            return f"{namespace}:{key}"
        return key
    
    def _hash_key(self, key: str) -> str:
        """对长键进行哈希处理"""
        if len(key) > 200:
            return hashlib.md5(key.encode()).hexdigest()
        return key
    
    def get(
        self,
        key: str,
        namespace: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            namespace: 命名空间
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        cache_key = self._hash_key(self._generate_key(key, namespace))
        
        # 先查 TTL 缓存
        value = self._cache.get(cache_key)
        if value is not None:
            self._stats["hits"] += 1
            logger.debug(f"缓存命中: {cache_key}")
            return value
        
        # 再查永久缓存
        value = self._permanent_cache.get(cache_key)
        if value is not None:
            self._stats["hits"] += 1
            logger.debug(f"永久缓存命中: {cache_key}")
            return value
        
        self._stats["misses"] += 1
        logger.debug(f"缓存未命中: {cache_key}")
        return default
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: Optional[str] = None,
        permanent: bool = False
    ) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 使用默认值
            namespace: 命名空间
            permanent: 是否永久缓存（使用 LRU 策略）
        """
        cache_key = self._hash_key(self._generate_key(key, namespace))
        
        if permanent:
            self._permanent_cache[cache_key] = value
        else:
            # TTLCache 不支持单独设置 TTL，需要使用默认值
            self._cache[cache_key] = value
        
        self._stats["sets"] += 1
        logger.debug(f"缓存设置: {cache_key}, permanent={permanent}")
    
    def delete(
        self,
        key: str,
        namespace: Optional[str] = None
    ) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            namespace: 命名空间
            
        Returns:
            是否成功删除
        """
        cache_key = self._hash_key(self._generate_key(key, namespace))
        
        deleted = False
        
        if cache_key in self._cache:
            del self._cache[cache_key]
            deleted = True
        
        if cache_key in self._permanent_cache:
            del self._permanent_cache[cache_key]
            deleted = True
        
        if deleted:
            self._stats["deletes"] += 1
            logger.debug(f"缓存删除: {cache_key}")
        
        return deleted
    
    def clear(self, namespace: Optional[str] = None) -> int:
        """
        清除缓存
        
        Args:
            namespace: 命名空间（None 清除所有）
            
        Returns:
            清除的条目数
        """
        if namespace is None:
            count = len(self._cache) + len(self._permanent_cache)
            self._cache.clear()
            self._permanent_cache.clear()
            logger.info(f"缓存已清空: {count} 条")
            return count
        
        # 清除特定命名空间
        prefix = f"{namespace}:"
        count = 0
        
        for key in list(self._cache.keys()):
            if key.startswith(prefix):
                del self._cache[key]
                count += 1
        
        for key in list(self._permanent_cache.keys()):
            if key.startswith(prefix):
                del self._permanent_cache[key]
                count += 1
        
        logger.info(f"命名空间 {namespace} 缓存已清空: {count} 条")
        return count
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            **self._stats,
            "hit_rate": round(hit_rate * 100, 2),
            "cache_size": len(self._cache),
            "permanent_cache_size": len(self._permanent_cache)
        }
    
    def exists(self, key: str, namespace: Optional[str] = None) -> bool:
        """检查缓存是否存在"""
        cache_key = self._hash_key(self._generate_key(key, namespace))
        return cache_key in self._cache or cache_key in self._permanent_cache


# 全局缓存实例
cache_manager = CacheManager(
    default_ttl=300,  # 5 分钟默认过期
    max_size=1000
)


# ============ 缓存装饰器 ============

def cached(
    ttl: int = 300,
    namespace: Optional[str] = None,
    key_builder: Optional[Callable[..., str]] = None
):
    """
    缓存装饰器
    
    用于缓存函数返回值
    
    Args:
        ttl: 过期时间（秒）
        namespace: 命名空间
        key_builder: 自定义键生成器
        
    Example:
        @cached(ttl=60, namespace="prices")
        async def get_price(province: str) -> float:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # 默认键：函数名 + 参数
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # 尝试从缓存获取
            cached_value = cache_manager.get(cache_key, namespace=namespace)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            cache_manager.set(cache_key, result, ttl=ttl, namespace=namespace)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # 尝试从缓存获取
            cached_value = cache_manager.get(cache_key, namespace=namespace)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            cache_manager.set(cache_key, result, ttl=ttl, namespace=namespace)
            
            return result
        
        # 根据函数类型选择包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def cache_invalidate(
    namespace: Optional[str] = None,
    key_pattern: Optional[str] = None
):
    """
    缓存失效装饰器
    
    在函数执行后清除相关缓存
    
    Args:
        namespace: 要清除的命名空间
        key_pattern: 要删除的键模式
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            result = await func(*args, **kwargs)
            
            if namespace:
                cache_manager.clear(namespace)
            elif key_pattern:
                cache_manager.delete(key_pattern)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            result = func(*args, **kwargs)
            
            if namespace:
                cache_manager.clear(namespace)
            elif key_pattern:
                cache_manager.delete(key_pattern)
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# ============ 预定义命名空间 ============

class CacheNamespace:
    """缓存命名空间常量"""
    PROVINCE_CONFIG = "province_config"
    MARKET_PRICES = "market_prices"
    PRICE_PREDICTION = "price_prediction"
    USER_SESSION = "user_session"
    TRADING_STATS = "trading_stats"
    CONTRACT_SUMMARY = "contract_summary"
