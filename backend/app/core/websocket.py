"""
PowerX WebSocket 管理器

创建日期: 2026-01-07
作者: zhi.qu

WebSocket 连接池管理、频道订阅、消息广播
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger


class Channel(str, Enum):
    """WebSocket 频道"""
    MARKET = "market"           # 市场数据
    ORDERS = "orders"           # 订单更新
    NOTIFICATIONS = "notifications"  # 系统通知
    HEARTBEAT = "heartbeat"     # 心跳


@dataclass
class Connection:
    """WebSocket 连接信息"""
    websocket: WebSocket
    user_id: Optional[str] = None
    channels: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def connection_id(self) -> str:
        """生成连接 ID"""
        return f"{id(self.websocket)}_{self.connected_at.timestamp()}"


class WebSocketManager:
    """
    WebSocket 连接管理器
    
    功能：
    - 连接池管理
    - 频道订阅/取消订阅
    - 消息广播
    - 心跳检测
    """
    
    def __init__(self):
        # 活跃连接: connection_id -> Connection
        self._connections: Dict[str, Connection] = {}
        
        # 频道订阅: channel -> Set[connection_id]
        self._channel_subscriptions: Dict[str, Set[str]] = {
            channel.value: set() for channel in Channel
        }
        
        # 用户连接映射: user_id -> Set[connection_id]
        self._user_connections: Dict[str, Set[str]] = {}
        
        # 心跳任务
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._heartbeat_interval = 30  # 秒
        self._heartbeat_timeout = 60   # 秒
        
        # 消息处理器
        self._message_handlers: Dict[str, Callable] = {}
        
        logger.info("WebSocket 管理器初始化")
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: Optional[str] = None,
        channels: Optional[List[str]] = None
    ) -> Connection:
        """
        接受新的 WebSocket 连接
        
        Args:
            websocket: WebSocket 实例
            user_id: 用户 ID
            channels: 初始订阅的频道列表
            
        Returns:
            Connection: 连接对象
        """
        await websocket.accept()
        
        connection = Connection(
            websocket=websocket,
            user_id=user_id,
            channels=set(channels or [])
        )
        
        connection_id = connection.connection_id
        self._connections[connection_id] = connection
        
        # 订阅频道
        for channel in connection.channels:
            self._subscribe_channel(connection_id, channel)
        
        # 记录用户连接
        if user_id:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(connection_id)
        
        logger.info(f"WebSocket 连接建立: {connection_id}, user={user_id}, channels={channels}")
        
        # 发送连接成功消息
        await self.send_personal(connection_id, {
            "type": "connected",
            "connection_id": connection_id,
            "channels": list(connection.channels),
            "timestamp": datetime.now().isoformat()
        })
        
        return connection
    
    async def disconnect(self, connection_id: str) -> None:
        """
        断开 WebSocket 连接
        
        Args:
            connection_id: 连接 ID
        """
        connection = self._connections.get(connection_id)
        if not connection:
            return
        
        # 从所有频道取消订阅
        for channel in list(connection.channels):
            self._unsubscribe_channel(connection_id, channel)
        
        # 移除用户连接映射
        if connection.user_id:
            user_connections = self._user_connections.get(connection.user_id, set())
            user_connections.discard(connection_id)
            if not user_connections:
                del self._user_connections[connection.user_id]
        
        # 移除连接
        del self._connections[connection_id]
        
        logger.info(f"WebSocket 连接断开: {connection_id}")
    
    def _subscribe_channel(self, connection_id: str, channel: str) -> None:
        """订阅频道"""
        if channel not in self._channel_subscriptions:
            self._channel_subscriptions[channel] = set()
        self._channel_subscriptions[channel].add(connection_id)
        
        connection = self._connections.get(connection_id)
        if connection:
            connection.channels.add(channel)
    
    def _unsubscribe_channel(self, connection_id: str, channel: str) -> None:
        """取消订阅频道"""
        if channel in self._channel_subscriptions:
            self._channel_subscriptions[channel].discard(connection_id)
        
        connection = self._connections.get(connection_id)
        if connection:
            connection.channels.discard(channel)
    
    async def subscribe(
        self,
        connection_id: str,
        channels: List[str]
    ) -> None:
        """
        订阅频道
        
        Args:
            connection_id: 连接 ID
            channels: 频道列表
        """
        for channel in channels:
            self._subscribe_channel(connection_id, channel)
        
        logger.debug(f"连接 {connection_id} 订阅频道: {channels}")
        
        await self.send_personal(connection_id, {
            "type": "subscribed",
            "channels": channels,
            "timestamp": datetime.now().isoformat()
        })
    
    async def unsubscribe(
        self,
        connection_id: str,
        channels: List[str]
    ) -> None:
        """
        取消订阅频道
        
        Args:
            connection_id: 连接 ID
            channels: 频道列表
        """
        for channel in channels:
            self._unsubscribe_channel(connection_id, channel)
        
        logger.debug(f"连接 {connection_id} 取消订阅频道: {channels}")
        
        await self.send_personal(connection_id, {
            "type": "unsubscribed",
            "channels": channels,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_personal(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        发送个人消息
        
        Args:
            connection_id: 连接 ID
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        connection = self._connections.get(connection_id)
        if not connection:
            return False
        
        try:
            await connection.websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {connection_id}, error={e}")
            await self.disconnect(connection_id)
            return False
    
    async def send_to_user(
        self,
        user_id: str,
        message: Dict[str, Any]
    ) -> int:
        """
        发送消息给指定用户的所有连接
        
        Args:
            user_id: 用户 ID
            message: 消息内容
            
        Returns:
            成功发送的连接数
        """
        connection_ids = self._user_connections.get(user_id, set())
        success_count = 0
        
        for connection_id in list(connection_ids):
            if await self.send_personal(connection_id, message):
                success_count += 1
        
        return success_count
    
    async def broadcast_channel(
        self,
        channel: str,
        message: Dict[str, Any],
        exclude: Optional[Set[str]] = None
    ) -> int:
        """
        向频道广播消息
        
        Args:
            channel: 频道名称
            message: 消息内容
            exclude: 排除的连接 ID 集合
            
        Returns:
            成功发送的连接数
        """
        connection_ids = self._channel_subscriptions.get(channel, set())
        exclude = exclude or set()
        success_count = 0
        
        # 添加频道信息到消息
        message["channel"] = channel
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        for connection_id in list(connection_ids):
            if connection_id not in exclude:
                if await self.send_personal(connection_id, message):
                    success_count += 1
        
        logger.debug(f"频道广播: {channel}, 发送: {success_count}/{len(connection_ids)}")
        return success_count
    
    async def broadcast_all(
        self,
        message: Dict[str, Any],
        exclude: Optional[Set[str]] = None
    ) -> int:
        """
        向所有连接广播消息
        
        Args:
            message: 消息内容
            exclude: 排除的连接 ID 集合
            
        Returns:
            成功发送的连接数
        """
        exclude = exclude or set()
        success_count = 0
        
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        for connection_id in list(self._connections.keys()):
            if connection_id not in exclude:
                if await self.send_personal(connection_id, message):
                    success_count += 1
        
        logger.debug(f"全局广播: 发送: {success_count}/{len(self._connections)}")
        return success_count
    
    async def handle_message(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> None:
        """
        处理收到的消息
        
        Args:
            connection_id: 连接 ID
            message: 消息内容
        """
        msg_type = message.get("type", "unknown")
        
        # 更新心跳时间
        connection = self._connections.get(connection_id)
        if connection:
            connection.last_heartbeat = datetime.now()
        
        # 处理心跳
        if msg_type == "ping":
            await self.send_personal(connection_id, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # 处理订阅/取消订阅
        if msg_type == "subscribe":
            channels = message.get("channels", [])
            await self.subscribe(connection_id, channels)
            return
        
        if msg_type == "unsubscribe":
            channels = message.get("channels", [])
            await self.unsubscribe(connection_id, channels)
            return
        
        # 调用自定义处理器
        handler = self._message_handlers.get(msg_type)
        if handler:
            await handler(connection_id, message)
        else:
            logger.warning(f"未知消息类型: {msg_type}")
    
    def register_handler(
        self,
        msg_type: str,
        handler: Callable[[str, Dict[str, Any]], Any]
    ) -> None:
        """
        注册消息处理器
        
        Args:
            msg_type: 消息类型
            handler: 处理函数
        """
        self._message_handlers[msg_type] = handler
        logger.debug(f"注册消息处理器: {msg_type}")
    
    async def start_heartbeat(self) -> None:
        """启动心跳检测任务"""
        if self._heartbeat_task is not None:
            return
        
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("心跳检测任务已启动")
    
    async def stop_heartbeat(self) -> None:
        """停止心跳检测任务"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None
            logger.info("心跳检测任务已停止")
    
    async def _heartbeat_loop(self) -> None:
        """心跳检测循环"""
        while True:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                await self._check_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳检测错误: {e}")
    
    async def _check_connections(self) -> None:
        """检查连接健康状态"""
        now = datetime.now()
        stale_connections = []
        
        for connection_id, connection in list(self._connections.items()):
            elapsed = (now - connection.last_heartbeat).total_seconds()
            if elapsed > self._heartbeat_timeout:
                stale_connections.append(connection_id)
        
        # 断开超时连接
        for connection_id in stale_connections:
            logger.warning(f"连接超时，断开: {connection_id}")
            await self.disconnect(connection_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        return {
            "total_connections": len(self._connections),
            "total_users": len(self._user_connections),
            "channels": {
                channel: len(subs) 
                for channel, subs in self._channel_subscriptions.items()
            }
        }


# 全局 WebSocket 管理器实例
ws_manager = WebSocketManager()
