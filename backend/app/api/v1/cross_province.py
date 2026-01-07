"""
PowerX 跨省交易 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.cross_province_service import get_cross_province_service

router = APIRouter(prefix="/cross-province", tags=["跨省交易"])


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    order_type: str  # buy/sell
    source_province: str
    target_province: str
    quantity: float
    price: float
    delivery_start: datetime
    delivery_end: datetime


class CrossProvinceOrderResponse(BaseModel):
    """订单响应"""
    order_id: str
    user_id: str
    order_type: str
    source_province: str
    target_province: str
    quantity: float
    price: float
    transmission_fee: float
    total_price: float
    status: str
    filled_quantity: float
    created_at: datetime


class ChannelResponse(BaseModel):
    """通道响应"""
    channel_id: str
    name: str
    from_province: str
    to_province: str
    capacity: float
    available_capacity: float
    transmission_fee: float
    loss_rate: float


@router.post("/orders", response_model=CrossProvinceOrderResponse)
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建跨省交易订单"""
    service = get_cross_province_service(db)
    
    order = await service.create_order(
        user_id="user-001",  # TODO: 从认证获取
        order_type=request.order_type,
        source_province=request.source_province,
        target_province=request.target_province,
        quantity=request.quantity,
        price=request.price,
        delivery_start=request.delivery_start,
        delivery_end=request.delivery_end
    )
    
    return CrossProvinceOrderResponse(
        order_id=order.order_id,
        user_id=order.user_id,
        order_type=order.order_type,
        source_province=order.source_province,
        target_province=order.target_province,
        quantity=order.quantity,
        price=order.price,
        transmission_fee=order.transmission_fee,
        total_price=order.total_price,
        status=order.status,
        filled_quantity=order.filled_quantity or 0,
        created_at=order.created_at
    )


@router.get("/orders", response_model=List[CrossProvinceOrderResponse])
async def list_orders(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取订单列表"""
    service = get_cross_province_service(db)
    orders = await service.get_user_orders(
        user_id="user-001",
        status=status
    )
    
    return [
        CrossProvinceOrderResponse(
            order_id=o.order_id,
            user_id=o.user_id,
            order_type=o.order_type,
            source_province=o.source_province,
            target_province=o.target_province,
            quantity=o.quantity,
            price=o.price,
            transmission_fee=o.transmission_fee,
            total_price=o.total_price,
            status=o.status,
            filled_quantity=o.filled_quantity or 0,
            created_at=o.created_at
        )
        for o in orders
    ]


@router.get("/orders/{order_id}", response_model=CrossProvinceOrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    service = get_cross_province_service(db)
    order = await service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    return CrossProvinceOrderResponse(
        order_id=order.order_id,
        user_id=order.user_id,
        order_type=order.order_type,
        source_province=order.source_province,
        target_province=order.target_province,
        quantity=order.quantity,
        price=order.price,
        transmission_fee=order.transmission_fee,
        total_price=order.total_price,
        status=order.status,
        filled_quantity=order.filled_quantity or 0,
        created_at=order.created_at
    )


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取消订单"""
    service = get_cross_province_service(db)
    success = await service.cancel_order(order_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="取消失败")
    
    return {"success": True, "message": "订单已取消"}


@router.post("/match")
async def match_orders(
    db: AsyncSession = Depends(get_db)
):
    """执行撮合"""
    service = get_cross_province_service(db)
    matches = await service.match_orders()
    
    return {
        "success": True,
        "matched_count": len(matches),
        "matches": matches
    }


@router.get("/channels", response_model=List[ChannelResponse])
async def list_channels(
    from_province: Optional[str] = None,
    to_province: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取输电通道列表"""
    service = get_cross_province_service(db)
    channels = await service.get_available_channels(from_province, to_province)
    
    return [
        ChannelResponse(
            channel_id=c.channel_id,
            name=c.name,
            from_province=c.from_province,
            to_province=c.to_province,
            capacity=c.capacity,
            available_capacity=c.available_capacity,
            transmission_fee=c.transmission_fee,
            loss_rate=c.loss_rate
        )
        for c in channels
    ]
