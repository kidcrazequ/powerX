"""
PowerX 历史数据回放服务
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import random


class HistoryReplayService:
    """历史数据回放服务"""
    
    def __init__(self):
        self._cache: Dict[str, List[Dict]] = {}
        logger.info("HistoryReplayService 初始化完成")
    
    async def get_available_dates(self, data_type: str = "market") -> List[str]:
        """获取可回放的日期列表"""
        dates = []
        today = datetime.now()
        for i in range(90):  # 最近90天
            date = today - timedelta(days=i+1)
            if date.weekday() < 5:  # 排除周末
                dates.append(date.strftime("%Y-%m-%d"))
        return dates
    
    async def get_replay_data(self, date: str, data_type: str = "market",
                             start_time: str = "09:00", end_time: str = "16:00",
                             interval_minutes: int = 5) -> List[Dict[str, Any]]:
        """获取指定日期的回放数据"""
        cache_key = f"{date}_{data_type}_{interval_minutes}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        data = await self._generate_mock_data(date, data_type, start_time, end_time, interval_minutes)
        self._cache[cache_key] = data
        return data
    
    async def _generate_mock_data(self, date: str, data_type: str,
                                  start_time: str, end_time: str,
                                  interval_minutes: int) -> List[Dict[str, Any]]:
        """生成模拟回放数据"""
        data = []
        base_price = 400 + random.uniform(-50, 50)
        base_volume = 1000
        
        # 解析时间
        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))
        
        current = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
        
        while current <= end:
            # 模拟价格波动
            price_change = random.gauss(0, 5)
            base_price = max(200, min(600, base_price + price_change))
            
            # 模拟成交量变化
            hour = current.hour
            volume_factor = 1.5 if hour in [9, 10, 14, 15] else 1.0  # 早盘和尾盘成交活跃
            volume = base_volume * volume_factor * (0.5 + random.random())
            
            data.append({
                "timestamp": current.strftime("%Y-%m-%d %H:%M:%S"),
                "time": current.strftime("%H:%M"),
                "price": round(base_price, 2),
                "volume": round(volume, 2),
                "high": round(base_price + random.uniform(0, 10), 2),
                "low": round(base_price - random.uniform(0, 10), 2),
                "open": round(base_price + random.uniform(-5, 5), 2),
                "close": round(base_price, 2),
                "change": round(price_change, 2),
                "change_percent": round(price_change / base_price * 100, 2)
            })
            
            current += timedelta(minutes=interval_minutes)
        
        return data
    
    async def get_trading_events(self, date: str) -> List[Dict[str, Any]]:
        """获取指定日期的交易事件"""
        events = []
        base_time = datetime.strptime(f"{date} 09:00", "%Y-%m-%d %H:%M")
        
        event_types = ["order_submit", "order_filled", "price_alert", "volume_spike"]
        
        for i in range(random.randint(20, 50)):
            event_time = base_time + timedelta(minutes=random.randint(0, 420))
            event_type = random.choice(event_types)
            
            events.append({
                "id": i + 1,
                "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": event_type,
                "description": self._get_event_description(event_type),
                "data": self._get_event_data(event_type)
            })
        
        # 按时间排序
        events.sort(key=lambda x: x["timestamp"])
        return events
    
    def _get_event_description(self, event_type: str) -> str:
        """获取事件描述"""
        descriptions = {
            "order_submit": "提交买入订单",
            "order_filled": "订单成交",
            "price_alert": "价格预警触发",
            "volume_spike": "成交量异常"
        }
        return descriptions.get(event_type, "未知事件")
    
    def _get_event_data(self, event_type: str) -> Dict:
        """获取事件数据"""
        if event_type in ["order_submit", "order_filled"]:
            return {
                "quantity": random.randint(100, 1000),
                "price": round(400 + random.uniform(-50, 50), 2),
                "direction": random.choice(["buy", "sell"])
            }
        elif event_type == "price_alert":
            return {
                "threshold": round(random.uniform(380, 420), 2),
                "current": round(random.uniform(370, 430), 2)
            }
        else:
            return {
                "volume": random.randint(5000, 20000),
                "avg_volume": random.randint(1000, 3000)
            }
    
    async def get_summary(self, date: str) -> Dict[str, Any]:
        """获取日期汇总"""
        data = await self.get_replay_data(date)
        if not data:
            return {}
        
        prices = [d["price"] for d in data]
        volumes = [d["volume"] for d in data]
        
        return {
            "date": date,
            "open_price": data[0]["price"],
            "close_price": data[-1]["price"],
            "high_price": max(prices),
            "low_price": min(prices),
            "total_volume": round(sum(volumes), 2),
            "avg_price": round(sum(prices) / len(prices), 2),
            "data_points": len(data),
            "price_range": round(max(prices) - min(prices), 2)
        }


history_replay_service = HistoryReplayService()


def get_history_replay_service() -> HistoryReplayService:
    return history_replay_service
