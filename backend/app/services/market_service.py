"""
PowerX 市场数据服务

创建日期: 2026-01-07
作者: zhi.qu

市场数据相关业务逻辑
支持数据缓存以提高性能
"""

import random
from datetime import date, datetime
from typing import List, Dict, Optional
from loguru import logger

from app.china_market.provinces import get_province_config, get_all_provinces
from app.china_market.price_cap import get_price_limits
from app.core.cache import cache_manager, cached, CacheNamespace


class MarketService:
    """市场数据服务"""
    
    # 模拟基准价格
    BASE_PRICES = {
        "广东": 485.0,
        "浙江": 492.0,
        "山东": 452.0,
        "山西": 435.0,
        "甘肃": 380.0
    }
    
    # 模拟24小时价格曲线模式（相对于基准价的百分比）
    HOURLY_PATTERN = [
        0.92, 0.88, 0.85, 0.82, 0.84, 0.86,  # 0-5点：低谷
        0.94, 1.03, 1.06, 1.08, 1.06, 1.04,  # 6-11点：早高峰
        1.02, 1.00, 0.98, 1.02, 1.08, 1.06,  # 12-17点：午后高峰
        1.04, 1.02, 0.98, 0.95, 0.92, 0.88   # 18-23点：晚间回落
    ]
    
    def __init__(self):
        logger.info("市场服务初始化")
    
    def get_supported_provinces(self) -> List[str]:
        """
        获取支持的省份列表
        
        使用永久缓存，因为省份配置不会频繁变化
        """
        cache_key = "supported_provinces"
        
        # 尝试从缓存获取
        cached_provinces = cache_manager.get(
            cache_key, 
            namespace=CacheNamespace.PROVINCE_CONFIG
        )
        if cached_provinces:
            return cached_provinces
        
        # 获取数据并缓存
        provinces = get_all_provinces()
        cache_manager.set(
            cache_key, 
            provinces, 
            namespace=CacheNamespace.PROVINCE_CONFIG,
            permanent=True  # 永久缓存
        )
        
        logger.debug(f"省份列表已缓存: {provinces}")
        return provinces
    
    async def get_market_summary(self, province: str) -> Optional[Dict]:
        """
        获取市场概览
        
        缓存 60 秒，因为概览数据更新不频繁
        
        Args:
            province: 省份名称
            
        Returns:
            市场概览数据
        """
        if province not in self.BASE_PRICES:
            logger.warning(f"不支持的省份: {province}")
            return None
        
        cache_key = f"summary:{province}"
        
        # 尝试从缓存获取
        cached_summary = cache_manager.get(
            cache_key, 
            namespace=CacheNamespace.MARKET_PRICES
        )
        if cached_summary:
            logger.debug(f"市场概览命中缓存: {province}")
            return cached_summary
        
        # 生成新数据
        base_price = self.BASE_PRICES[province]
        hourly_prices = self._generate_hourly_prices(province)
        
        summary = {
            "province": province,
            "avg_price": round(sum(hourly_prices) / len(hourly_prices), 2),
            "max_price": max(hourly_prices),
            "min_price": min(hourly_prices),
            "total_volume": random.randint(100000, 200000),
            "price_change_percent": round(random.uniform(-5, 5), 2),
            "updated_at": datetime.now().isoformat()
        }
        
        # 缓存结果
        cache_manager.set(
            cache_key, 
            summary, 
            ttl=60,  # 60秒过期
            namespace=CacheNamespace.MARKET_PRICES
        )
        
        logger.info(f"市场概览已生成并缓存: {province}")
        return summary
    
    async def get_historical_prices(
        self,
        province: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """
        获取历史价格数据
        
        缓存 60 秒
        
        Args:
            province: 省份名称
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            历史价格列表
        """
        target_date = (start_date or date.today()).isoformat()
        cache_key = f"history:{province}:{target_date}"
        
        # 尝试从缓存获取
        cached_prices = cache_manager.get(
            cache_key, 
            namespace=CacheNamespace.MARKET_PRICES
        )
        if cached_prices:
            logger.debug(f"历史价格命中缓存: {province} {target_date}")
            return cached_prices
        
        # 生成新数据
        prices = []
        base_price = self.BASE_PRICES.get(province, 480)
        
        for hour in range(24):
            day_ahead = base_price * self.HOURLY_PATTERN[hour] + random.uniform(-10, 10)
            realtime = day_ahead + random.uniform(-5, 5)
            
            prices.append({
                "province": province,
                "date": target_date,
                "hour": hour,
                "day_ahead_price": round(day_ahead, 2),
                "realtime_price": round(realtime, 2),
                "volume_mwh": random.randint(500, 2000)
            })
        
        # 缓存结果
        cache_manager.set(
            cache_key, 
            prices, 
            ttl=60,
            namespace=CacheNamespace.MARKET_PRICES
        )
        
        logger.info(f"历史价格已生成并缓存: {province} {target_date}")
        return prices
    
    async def get_hourly_prices(
        self,
        province: str,
        target_date: Optional[date] = None
    ) -> Dict:
        """
        获取24小时价格曲线
        
        缓存 60 秒
        
        Args:
            province: 省份名称
            target_date: 目标日期
            
        Returns:
            小时价格数据
        """
        date_str = (target_date or date.today()).isoformat()
        cache_key = f"hourly:{province}:{date_str}"
        
        # 尝试从缓存获取
        cached_hourly = cache_manager.get(
            cache_key, 
            namespace=CacheNamespace.MARKET_PRICES
        )
        if cached_hourly:
            logger.debug(f"小时价格命中缓存: {province} {date_str}")
            return cached_hourly
        
        # 生成新数据
        hourly_prices = self._generate_hourly_prices(province)
        
        result = {
            "province": province,
            "date": date_str,
            "prices": hourly_prices,
            "generated_at": datetime.now().isoformat()
        }
        
        # 缓存结果
        cache_manager.set(
            cache_key, 
            result, 
            ttl=60,
            namespace=CacheNamespace.MARKET_PRICES
        )
        
        logger.info(f"小时价格已生成并缓存: {province} {date_str}")
        return result
    
    async def get_realtime_price(self, province: str) -> Dict:
        """
        获取实时价格（模拟）
        
        短期缓存 5 秒，平衡实时性和性能
        
        Args:
            province: 省份名称
            
        Returns:
            实时价格数据
        """
        cache_key = f"realtime:{province}"
        
        # 尝试从缓存获取（5秒内的数据视为实时）
        cached_realtime = cache_manager.get(
            cache_key, 
            namespace=CacheNamespace.MARKET_PRICES
        )
        if cached_realtime:
            return cached_realtime
        
        # 生成新的实时价格
        base_price = self.BASE_PRICES.get(province, 480)
        current_hour = datetime.now().hour
        
        price = base_price * self.HOURLY_PATTERN[current_hour]
        price += random.uniform(-15, 15)
        
        result = {
            "price": round(price, 2),
            "change_percent": round(random.uniform(-3, 3), 2),
            "timestamp": datetime.now().isoformat()
        }
        
        # 短期缓存
        cache_manager.set(
            cache_key, 
            result, 
            ttl=5,  # 5秒过期
            namespace=CacheNamespace.MARKET_PRICES
        )
        
        return result
    
    def _generate_hourly_prices(self, province: str) -> List[float]:
        """
        生成24小时价格曲线
        
        Args:
            province: 省份名称
            
        Returns:
            24小时价格列表
        """
        base_price = self.BASE_PRICES.get(province, 480)
        min_price, max_price = get_price_limits(province)
        
        prices = []
        for hour in range(24):
            price = base_price * self.HOURLY_PATTERN[hour]
            price += random.uniform(-20, 20)
            
            # 山东允许负电价，凌晨时段可能出现负价
            if province == "山东" and hour in [3, 4, 5] and random.random() < 0.2:
                price = random.uniform(-50, 50)
            
            # 限价约束
            price = max(min_price, min(max_price, price))
            prices.append(round(price, 2))
        
        return prices
    
    def clear_cache(self, province: Optional[str] = None) -> int:
        """
        清除市场数据缓存
        
        Args:
            province: 省份（None 清除所有）
            
        Returns:
            清除的条目数
        """
        if province:
            # 清除特定省份的缓存
            count = 0
            for key_type in ["summary", "history", "hourly", "realtime"]:
                if cache_manager.delete(
                    f"{key_type}:{province}", 
                    namespace=CacheNamespace.MARKET_PRICES
                ):
                    count += 1
            logger.info(f"已清除 {province} 省份缓存: {count} 条")
            return count
        
        # 清除所有市场价格缓存
        count = cache_manager.clear(namespace=CacheNamespace.MARKET_PRICES)
        logger.info(f"已清除所有市场价格缓存: {count} 条")
        return count


# 创建服务实例
market_service = MarketService()