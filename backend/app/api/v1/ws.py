"""
PowerX WebSocket 路由

创建日期: 2026-01-07
作者: zhi.qu

WebSocket 端点定义
"""

import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from loguru import logger

from app.core.websocket import ws_manager, Channel
from app.core.security import decode_token

router = APIRouter()


async def get_user_from_token(token: Optional[str]) -> Optional[str]:
    """
    从 token 获取用户 ID
    
    Args:
        token: JWT token
        
    Returns:
        用户 ID 或 None
    """
    if not token:
        return None
    
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except Exception:
        return None


@router.websocket("/market/{province}")
async def websocket_market(
    websocket: WebSocket,
    province: str,
    token: Optional[str] = Query(None)
):
    """
    市场数据 WebSocket 端点
    
    订阅指定省份的实时市场数据
    
    Args:
        websocket: WebSocket 连接
        province: 省份名称
        token: 可选的认证 token
    """
    user_id = await get_user_from_token(token)
    
    # 创建频道名称: market:province
    channel = f"{Channel.MARKET.value}:{province}"
    
    connection = await ws_manager.connect(
        websocket=websocket,
        user_id=user_id,
        channels=[channel]
    )
    
    connection_id = connection.connection_id
    logger.info(f"市场 WebSocket 连接: province={province}, user={user_id}")
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await ws_manager.handle_message(connection_id, message)
            except json.JSONDecodeError:
                await ws_manager.send_personal(connection_id, {
                    "type": "error",
                    "message": "无效的 JSON 格式"
                })
    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
        logger.info(f"市场 WebSocket 断开: province={province}")


@router.websocket("/orders")
async def websocket_orders(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    订单更新 WebSocket 端点
    
    接收用户订单状态更新
    
    Args:
        websocket: WebSocket 连接
        token: 认证 token（推荐）
    """
    user_id = await get_user_from_token(token)
    
    if not user_id:
        await websocket.close(code=4001, reason="需要认证")
        return
    
    # 用户专属订单频道
    channel = f"{Channel.ORDERS.value}:{user_id}"
    
    connection = await ws_manager.connect(
        websocket=websocket,
        user_id=user_id,
        channels=[channel]
    )
    
    connection_id = connection.connection_id
    logger.info(f"订单 WebSocket 连接: user={user_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await ws_manager.handle_message(connection_id, message)
            except json.JSONDecodeError:
                await ws_manager.send_personal(connection_id, {
                    "type": "error",
                    "message": "无效的 JSON 格式"
                })
    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
        logger.info(f"订单 WebSocket 断开: user={user_id}")


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    系统通知 WebSocket 端点
    
    接收系统通知和警报
    
    Args:
        websocket: WebSocket 连接
        token: 可选的认证 token
    """
    user_id = await get_user_from_token(token)
    
    channels = [Channel.NOTIFICATIONS.value]
    
    # 如果已认证，还订阅用户专属通知
    if user_id:
        channels.append(f"{Channel.NOTIFICATIONS.value}:{user_id}")
    
    connection = await ws_manager.connect(
        websocket=websocket,
        user_id=user_id,
        channels=channels
    )
    
    connection_id = connection.connection_id
    logger.info(f"通知 WebSocket 连接: user={user_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await ws_manager.handle_message(connection_id, message)
            except json.JSONDecodeError:
                await ws_manager.send_personal(connection_id, {
                    "type": "error",
                    "message": "无效的 JSON 格式"
                })
    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
        logger.info(f"通知 WebSocket 断开: user={user_id}")


@router.websocket("/")
async def websocket_main(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    通用 WebSocket 端点
    
    支持动态订阅多个频道
    
    Args:
        websocket: WebSocket 连接
        token: 可选的认证 token
    """
    user_id = await get_user_from_token(token)
    
    connection = await ws_manager.connect(
        websocket=websocket,
        user_id=user_id,
        channels=[]
    )
    
    connection_id = connection.connection_id
    logger.info(f"通用 WebSocket 连接: user={user_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await ws_manager.handle_message(connection_id, message)
            except json.JSONDecodeError:
                await ws_manager.send_personal(connection_id, {
                    "type": "error",
                    "message": "无效的 JSON 格式"
                })
    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
        logger.info(f"通用 WebSocket 断开: user={user_id}")
