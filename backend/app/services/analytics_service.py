"""
PowerX 数据分析服务

创建日期: 2026-01-07
作者: zhi.qu

提供交易绩效、收益分析和趋势分析功能
"""

import random
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional
from loguru import logger

from app.services.market_service import market_service


class AnalyticsService:
    """
    数据分析服务
    
    功能：
    - 交易绩效分析
    - 收益归因分析
    - 趋势分析
    - 对比分析
    """
    
    def __init__(self):
        logger.info("数据分析服务初始化")
    
    async def get_trading_performance(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        province: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取交易绩效分析
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            province: 省份
            
        Returns:
            Dict: 绩效分析结果
        """
        logger.info(f"交易绩效分析: user={user_id}, province={province}")
        
        # 模拟绩效数据
        total_trades = random.randint(50, 200)
        win_trades = int(total_trades * random.uniform(0.55, 0.75))
        
        total_volume = random.uniform(5000, 20000)
        total_profit = random.uniform(-50000, 200000)
        
        return {
            "period": {
                "start": (start_date or date.today() - timedelta(days=30)).isoformat(),
                "end": (end_date or date.today()).isoformat()
            },
            "summary": {
                "total_trades": total_trades,
                "win_trades": win_trades,
                "loss_trades": total_trades - win_trades,
                "win_rate": round(win_trades / total_trades * 100, 2),
                "total_volume_mwh": round(total_volume, 2),
                "total_profit": round(total_profit, 2),
                "avg_profit_per_trade": round(total_profit / total_trades, 2)
            },
            "by_type": {
                "day_ahead": {
                    "trades": int(total_trades * 0.6),
                    "volume": round(total_volume * 0.6, 2),
                    "profit": round(total_profit * 0.7, 2)
                },
                "realtime": {
                    "trades": int(total_trades * 0.4),
                    "volume": round(total_volume * 0.4, 2),
                    "profit": round(total_profit * 0.3, 2)
                }
            },
            "by_direction": {
                "buy": {
                    "trades": int(total_trades * 0.55),
                    "volume": round(total_volume * 0.55, 2),
                    "avg_price": round(random.uniform(400, 500), 2)
                },
                "sell": {
                    "trades": int(total_trades * 0.45),
                    "volume": round(total_volume * 0.45, 2),
                    "avg_price": round(random.uniform(420, 520), 2)
                }
            },
            "daily_performance": self._generate_daily_performance(30),
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_profit_attribution(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        获取收益归因分析
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 收益归因结果
        """
        logger.info(f"收益归因分析: user={user_id}")
        
        total_profit = random.uniform(50000, 200000)
        
        # 归因分解
        price_diff_profit = total_profit * random.uniform(0.4, 0.6)
        timing_profit = total_profit * random.uniform(0.15, 0.3)
        volume_profit = total_profit * random.uniform(0.1, 0.2)
        strategy_profit = total_profit - price_diff_profit - timing_profit - volume_profit
        
        return {
            "total_profit": round(total_profit, 2),
            "attribution": {
                "price_difference": {
                    "amount": round(price_diff_profit, 2),
                    "percentage": round(price_diff_profit / total_profit * 100, 1),
                    "description": "买卖价差收益"
                },
                "timing": {
                    "amount": round(timing_profit, 2),
                    "percentage": round(timing_profit / total_profit * 100, 1),
                    "description": "时机选择收益"
                },
                "volume": {
                    "amount": round(volume_profit, 2),
                    "percentage": round(volume_profit / total_profit * 100, 1),
                    "description": "交易量贡献"
                },
                "strategy": {
                    "amount": round(strategy_profit, 2),
                    "percentage": round(strategy_profit / total_profit * 100, 1),
                    "description": "策略贡献"
                }
            },
            "benchmark_comparison": {
                "market_avg_return": round(random.uniform(3, 8), 2),
                "user_return": round(random.uniform(5, 15), 2),
                "excess_return": round(random.uniform(1, 7), 2)
            },
            "risk_adjusted_metrics": {
                "sharpe_ratio": round(random.uniform(0.5, 2.0), 2),
                "sortino_ratio": round(random.uniform(0.8, 2.5), 2),
                "max_drawdown": round(random.uniform(5, 15), 2)
            },
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_trend_analysis(
        self,
        province: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取趋势分析
        
        Args:
            province: 省份
            days: 分析天数
            
        Returns:
            Dict: 趋势分析结果
        """
        logger.info(f"趋势分析: province={province}, days={days}")
        
        # 获取历史数据
        prices = await market_service.get_historical_prices(province)
        
        # 生成趋势数据
        daily_data = []
        base_price = 450
        
        for i in range(days):
            target_date = date.today() - timedelta(days=days - i - 1)
            price = base_price + random.uniform(-30, 30) + i * random.uniform(-0.5, 0.5)
            volume = random.randint(50000, 150000)
            
            daily_data.append({
                "date": target_date.isoformat(),
                "avg_price": round(price, 2),
                "max_price": round(price + random.uniform(20, 50), 2),
                "min_price": round(price - random.uniform(20, 50), 2),
                "volume": volume
            })
        
        # 计算趋势指标
        prices_list = [d["avg_price"] for d in daily_data]
        volumes_list = [d["volume"] for d in daily_data]
        
        return {
            "province": province,
            "period": {
                "start": daily_data[0]["date"],
                "end": daily_data[-1]["date"]
            },
            "summary": {
                "avg_price": round(sum(prices_list) / len(prices_list), 2),
                "max_price": round(max(prices_list), 2),
                "min_price": round(min(prices_list), 2),
                "price_volatility": round(self._calculate_volatility(prices_list), 2),
                "total_volume": sum(volumes_list),
                "avg_daily_volume": round(sum(volumes_list) / len(volumes_list), 0)
            },
            "trend": {
                "direction": "上涨" if prices_list[-1] > prices_list[0] else "下跌",
                "change_percent": round((prices_list[-1] - prices_list[0]) / prices_list[0] * 100, 2),
                "trend_strength": random.choice(["强", "中", "弱"])
            },
            "moving_averages": {
                "ma5": round(sum(prices_list[-5:]) / 5, 2) if len(prices_list) >= 5 else None,
                "ma10": round(sum(prices_list[-10:]) / 10, 2) if len(prices_list) >= 10 else None,
                "ma20": round(sum(prices_list[-20:]) / 20, 2) if len(prices_list) >= 20 else None
            },
            "daily_data": daily_data,
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_comparison_analysis(
        self,
        provinces: List[str],
        metric: str = "price",
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取对比分析
        
        Args:
            provinces: 省份列表
            metric: 对比指标
            days: 分析天数
            
        Returns:
            Dict: 对比分析结果
        """
        logger.info(f"对比分析: provinces={provinces}, metric={metric}")
        
        comparison_data = {}
        
        for province in provinces:
            base_price = market_service.BASE_PRICES.get(province, 450)
            
            daily_prices = []
            for i in range(days):
                price = base_price + random.uniform(-30, 30)
                daily_prices.append({
                    "date": (date.today() - timedelta(days=days - i - 1)).isoformat(),
                    "value": round(price, 2)
                })
            
            comparison_data[province] = {
                "avg_value": round(sum(p["value"] for p in daily_prices) / len(daily_prices), 2),
                "max_value": max(p["value"] for p in daily_prices),
                "min_value": min(p["value"] for p in daily_prices),
                "daily_data": daily_prices
            }
        
        # 排名
        ranking = sorted(
            comparison_data.items(),
            key=lambda x: x[1]["avg_value"],
            reverse=True
        )
        
        return {
            "metric": metric,
            "period": {
                "start": (date.today() - timedelta(days=days)).isoformat(),
                "end": date.today().isoformat()
            },
            "data": comparison_data,
            "ranking": [{"province": p, "avg_value": d["avg_value"], "rank": i + 1} for i, (p, d) in enumerate(ranking)],
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_hourly_pattern(
        self,
        province: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取小时模式分析
        
        Args:
            province: 省份
            days: 分析天数
            
        Returns:
            Dict: 小时模式分析结果
        """
        logger.info(f"小时模式分析: province={province}")
        
        base_price = market_service.BASE_PRICES.get(province, 450)
        hourly_pattern = market_service.HOURLY_PATTERN
        
        hourly_stats = []
        for hour in range(24):
            avg_price = base_price * hourly_pattern[hour]
            
            hourly_stats.append({
                "hour": hour,
                "avg_price": round(avg_price, 2),
                "volatility": round(random.uniform(5, 20), 2),
                "volume_share": round(random.uniform(3, 6), 2)
            })
        
        # 识别高峰和低谷时段
        sorted_hours = sorted(hourly_stats, key=lambda x: x["avg_price"], reverse=True)
        peak_hours = [h["hour"] for h in sorted_hours[:4]]
        valley_hours = [h["hour"] for h in sorted_hours[-4:]]
        
        return {
            "province": province,
            "hourly_stats": hourly_stats,
            "peak_hours": peak_hours,
            "valley_hours": valley_hours,
            "peak_valley_spread": round(sorted_hours[0]["avg_price"] - sorted_hours[-1]["avg_price"], 2),
            "recommendations": [
                f"建议在 {valley_hours[0]}:00-{valley_hours[1]}:00 时段买入",
                f"建议在 {peak_hours[0]}:00-{peak_hours[1]}:00 时段卖出",
                f"峰谷价差约 {round(sorted_hours[0]['avg_price'] - sorted_hours[-1]['avg_price'], 2)} 元/MWh"
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_daily_performance(self, days: int) -> List[Dict]:
        """生成每日绩效数据"""
        data = []
        cumulative_profit = 0
        
        for i in range(days):
            daily_profit = random.uniform(-5000, 8000)
            cumulative_profit += daily_profit
            
            data.append({
                "date": (date.today() - timedelta(days=days - i - 1)).isoformat(),
                "daily_profit": round(daily_profit, 2),
                "cumulative_profit": round(cumulative_profit, 2),
                "trades": random.randint(1, 10)
            })
        
        return data
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """计算波动率"""
        if len(prices) < 2:
            return 0
        
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i - 1]) / prices[i - 1]
            returns.append(ret)
        
        if not returns:
            return 0
        
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        
        return (variance ** 0.5) * 100


# 全局分析服务实例
analytics_service = AnalyticsService()
