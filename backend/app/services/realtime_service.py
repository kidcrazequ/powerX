"""
PowerX 实时数据推送服务

创建日期: 2026-01-07
作者: zhi.qu

生成模拟实时数据并通过 WebSocket 广播
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, Optional, Set
from loguru import logger

from app.core.websocket import ws_manager, Channel
from app.services.market_service import MarketService


class RealtimeService:
    """
    实时数据推送服务
    
    功能：
    - 模拟生成实时市场价格
    - 定时广播价格更新
    - 发送订单状态更新
    - 推送系统通知
    """
    
    def __init__(self):
        self.market_service = MarketService()
        self._running = False
        self._price_task: Optional[asyncio.Task] = None
        self._update_interval = 5  # 价格更新间隔（秒）
        
        # 追踪的省份
        self._active_provinces: Set[str] = {"广东", "浙江", "山东", "山西", "甘肃"}
        
        # 当前价格状态
        self._current_prices: Dict[str, float] = {}
        
        logger.info("实时数据服务初始化")
    
    async def start(self) -> None:
        """启动实时数据推送"""
        if self._running:
            logger.warning("实时数据服务已在运行")
            return
        
        self._running = True
        self._price_task = asyncio.create_task(self._price_update_loop())
        
        # 启动 WebSocket 心跳检测
        await ws_manager.start_heartbeat()
        
        logger.info("实时数据服务已启动")
    
    async def stop(self) -> None:
        """停止实时数据推送"""
        self._running = False
        
        if self._price_task:
            self._price_task.cancel()
            try:
                await self._price_task
            except asyncio.CancelledError:
                pass
            self._price_task = None
        
        await ws_manager.stop_heartbeat()
        
        logger.info("实时数据服务已停止")
    
    async def _price_update_loop(self) -> None:
        """价格更新循环"""
        while self._running:
            try:
                await self._broadcast_prices()
                await asyncio.sleep(self._update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"价格更新错误: {e}")
                await asyncio.sleep(1)
    
    async def _broadcast_prices(self) -> None:
        """广播所有省份的价格更新"""
        for province in self._active_provinces:
            try:
                price_data = await self._generate_price_update(province)
                
                # 广播到省份专属频道
                channel = f"{Channel.MARKET.value}:{province}"
                await ws_manager.broadcast_channel(channel, {
                    "type": "price_update",
                    "data": price_data
                })
            except Exception as e:
                logger.error(f"广播 {province} 价格失败: {e}")
    
    async def _generate_price_update(self, province: str) -> Dict:
        """
        生成价格更新数据
        
        Args:
            province: 省份名称
            
        Returns:
            价格更新数据
        """
        # 获取基准价格
        base_prices = {
            "广东": 485.0,
            "浙江": 492.0,
            "山东": 452.0,
            "山西": 435.0,
            "甘肃": 380.0
        }
        
        base_price = base_prices.get(province, 480.0)
        
        # 获取或初始化当前价格
        if province not in self._current_prices:
            self._current_prices[province] = base_price
        
        prev_price = self._current_prices[province]
        
        # 生成新价格（在前一价格基础上小幅波动）
        change = random.gauss(0, 3)  # 正态分布波动
        new_price = prev_price + change
        
        # 限制价格范围
        min_price = base_price * 0.7
        max_price = base_price * 1.5
        new_price = max(min_price, min(max_price, new_price))
        
        self._current_prices[province] = new_price
        
        # 计算变化百分比
        change_percent = ((new_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
        
        # 确定趋势
        if change_percent > 0.1:
            trend = "up"
        elif change_percent < -0.1:
            trend = "down"
        else:
            trend = "stable"
        
        return {
            "province": province,
            "price": round(new_price, 2),
            "prev_price": round(prev_price, 2),
            "change_percent": round(change_percent, 2),
            "trend": trend,
            "volume": random.randint(500, 2000),
            "timestamp": datetime.now().isoformat()
        }
    
    async def send_order_update(
        self,
        user_id: str,
        order_id: str,
        status: str,
        filled_quantity: Optional[float] = None,
        filled_price: Optional[float] = None,
        message: Optional[str] = None
    ) -> int:
        """
        发送订单状态更新
        
        Args:
            user_id: 用户 ID
            order_id: 订单 ID
            status: 订单状态
            filled_quantity: 成交数量
            filled_price: 成交价格
            message: 附加消息
            
        Returns:
            发送成功的连接数
        """
        update_data = {
            "type": "order_update",
            "data": {
                "order_id": order_id,
                "status": status,
                "filled_quantity": filled_quantity,
                "filled_price": filled_price,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # 发送到用户专属订单频道
        channel = f"{Channel.ORDERS.value}:{user_id}"
        count = await ws_manager.broadcast_channel(channel, update_data)
        
        logger.info(f"订单更新已发送: order={order_id}, user={user_id}, status={status}")
        return count
    
    async def send_notification(
        self,
        notification_type: str,
        title: str,
        message: str,
        user_id: Optional[str] = None,
        data: Optional[Dict] = None
    ) -> int:
        """
        发送系统通知
        
        Args:
            notification_type: 通知类型 (info, warning, error, success)
            title: 通知标题
            message: 通知内容
            user_id: 目标用户（None 表示广播给所有人）
            data: 附加数据
            
        Returns:
            发送成功的连接数
        """
        notification_data = {
            "type": "notification",
            "data": {
                "type": notification_type,
                "title": title,
                "message": message,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if user_id:
            # 发送给特定用户
            channel = f"{Channel.NOTIFICATIONS.value}:{user_id}"
            count = await ws_manager.broadcast_channel(channel, notification_data)
        else:
            # 广播给所有人
            count = await ws_manager.broadcast_channel(
                Channel.NOTIFICATIONS.value, 
                notification_data
            )
        
        logger.info(f"通知已发送: type={notification_type}, title={title}, user={user_id}")
        return count
    
    async def send_price_alert(
        self,
        province: str,
        alert_type: str,
        price: float,
        threshold: float,
        message: str
    ) -> int:
        """
        发送价格预警
        
        Args:
            province: 省份
            alert_type: 预警类型 (high_price, low_price, volatility)
            price: 当前价格
            threshold: 预警阈值
            message: 预警消息
            
        Returns:
            发送成功的连接数
        """
        alert_data = {
            "type": "price_alert",
            "data": {
                "province": province,
                "alert_type": alert_type,
                "price": price,
                "threshold": threshold,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # 广播到省份频道
        channel = f"{Channel.MARKET.value}:{province}"
        count = await ws_manager.broadcast_channel(channel, alert_data)
        
        # 同时发送到通知频道
        await ws_manager.broadcast_channel(Channel.NOTIFICATIONS.value, alert_data)
        
        logger.warning(f"价格预警已发送: province={province}, type={alert_type}, price={price}")
        return count
    
    def get_current_prices(self) -> Dict[str, float]:
        """获取当前所有省份的价格"""
        return self._current_prices.copy()
    
    def get_stats(self) -> Dict:
        """获取服务统计信息"""
        return {
            "running": self._running,
            "update_interval": self._update_interval,
            "active_provinces": list(self._active_provinces),
            "current_prices": self._current_prices,
            "websocket_stats": ws_manager.get_stats()
        }


# 全局实时服务实例
realtime_service = RealtimeService()
