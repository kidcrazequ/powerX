"""
PowerX 交易 API

创建日期: 2026-01-07
作者: zhi.qu

交易订单相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from enum import Enum

from app.services.trading_service import TradingService
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# ============ 枚举类型 ============

class MarketType(str, Enum):
    DAY_AHEAD = "DAY_AHEAD"
    INTRADAY = "INTRADAY"


class Direction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


# ============ 请求/响应模型 ============

class OrderCreateRequest(BaseModel):
    """创建订单请求"""
    province: str
    market_type: MarketType
    direction: Direction
    price: float
    quantity_mwh: float


class OrderResponse(BaseModel):
    """订单响应"""
    id: str
    province: str
    market_type: str
    direction: str
    price: float
    quantity_mwh: float
    filled_quantity: float
    filled_price: Optional[float]
    status: str
    created_at: str


class PositionResponse(BaseModel):
    """持仓响应"""
    id: str
    contract: str
    direction: str
    quantity_mwh: float
    avg_price: float
    current_price: float
    pnl: float
    pnl_percent: float


# ============ API 端点 ============

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    request: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建交易订单
    
    在现货市场提交买入或卖出订单
    """
    service = TradingService(db)
    
    try:
        order = await service.create_order(
            user_id=current_user.id,
            province=request.province,
            market_type=request.market_type.value,
            direction=request.direction.value,
            price=request.price,
            quantity_mwh=request.quantity_mwh
        )
        
        return OrderResponse(
            id=order["id"],
            province=order["province"],
            market_type=order["market_type"],
            direction=order["direction"],
            price=order["price"],
            quantity_mwh=order["quantity_mwh"],
            filled_quantity=order.get("filled_quantity", 0),
            filled_price=order.get("filled_price"),
            status=order["status"],
            created_at=order["created_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    market_type: Optional[MarketType] = None,
    status: Optional[OrderStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取订单列表
    
    查询当前用户的历史订单
    """
    service = TradingService(db)
    
    orders = await service.get_orders(
        user_id=current_user.id,
        market_type=market_type.value if market_type else None,
        status=status.value if status else None,
        start_date=start_date,
        end_date=end_date
    )
    
    return [
        OrderResponse(
            id=o["id"],
            province=o["province"],
            market_type=o["market_type"],
            direction=o["direction"],
            price=o["price"],
            quantity_mwh=o["quantity_mwh"],
            filled_quantity=o.get("filled_quantity", 0),
            filled_price=o.get("filled_price"),
            status=o["status"],
            created_at=o["created_at"]
        )
        for o in orders
    ]


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取订单详情
    """
    service = TradingService(db)
    order = await service.get_order(order_id, current_user.id)
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    return OrderResponse(
        id=order["id"],
        province=order["province"],
        market_type=order["market_type"],
        direction=order["direction"],
        price=order["price"],
        quantity_mwh=order["quantity_mwh"],
        filled_quantity=order.get("filled_quantity", 0),
        filled_price=order.get("filled_price"),
        status=order["status"],
        created_at=order["created_at"]
    )


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    撤销订单
    
    撤销未成交或部分成交的订单
    """
    service = TradingService(db)
    
    try:
        await service.cancel_order(order_id, current_user.id)
        return {"message": "订单已撤销", "order_id": order_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"撤销订单失败: {str(e)}")


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取持仓列表
    """
    service = TradingService(db)
    positions = await service.get_positions(current_user.id)
    
    return [
        PositionResponse(
            id=p["id"],
            contract=p["contract"],
            direction=p["direction"],
            quantity_mwh=p["quantity_mwh"],
            avg_price=p["avg_price"],
            current_price=p["current_price"],
            pnl=p["pnl"],
            pnl_percent=p["pnl_percent"]
        )
        for p in positions
    ]


@router.get("/statistics")
async def get_trading_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取交易统计
    """
    service = TradingService(db)
    stats = await service.get_statistics(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return stats
