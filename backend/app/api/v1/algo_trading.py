"""
PowerX 算法交易 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.algo_trading_service import get_algo_trading_service

router = APIRouter(prefix="/algo-trading", tags=["算法交易"])


class TWAPOrderCreate(BaseModel):
    order_type: str  # buy, sell
    target_quantity: float
    duration_minutes: int
    slice_count: Optional[int] = None
    price_limit_upper: Optional[float] = None
    price_limit_lower: Optional[float] = None
    province: str = "guangdong"
    market_type: str = "spot"


class VWAPOrderCreate(BaseModel):
    order_type: str
    target_quantity: float
    duration_minutes: int
    volume_profile: Optional[List[float]] = None
    price_limit_upper: Optional[float] = None
    price_limit_lower: Optional[float] = None
    province: str = "guangdong"
    market_type: str = "spot"


class IcebergOrderCreate(BaseModel):
    order_type: str
    target_quantity: float
    visible_quantity: float
    price: float
    province: str = "guangdong"
    market_type: str = "spot"


class AlgoOrderResponse(BaseModel):
    algo_id: str
    algo_type: str
    algo_params: Optional[dict]
    province: str
    market_type: str
    order_type: str
    target_quantity: float
    target_price: Optional[float]
    status: str
    filled_quantity: float
    avg_price: Optional[float]
    slices_total: int
    slices_filled: int

    class Config:
        from_attributes = True


class AlgoSliceResponse(BaseModel):
    slice_id: str
    sequence: int
    quantity: float
    price: Optional[float]
    status: str
    filled_quantity: float
    filled_price: Optional[float]

    class Config:
        from_attributes = True


@router.post("/twap", response_model=AlgoOrderResponse)
async def create_twap_order(
    data: TWAPOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建 TWAP 订单"""
    service = get_algo_trading_service(db)
    order = await service.create_twap_order(
        user_id="current_user",
        **data.model_dump()
    )
    return order


@router.post("/vwap", response_model=AlgoOrderResponse)
async def create_vwap_order(
    data: VWAPOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建 VWAP 订单"""
    service = get_algo_trading_service(db)
    order = await service.create_vwap_order(
        user_id="current_user",
        **data.model_dump()
    )
    return order


@router.post("/iceberg", response_model=AlgoOrderResponse)
async def create_iceberg_order(
    data: IcebergOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建冰山订单"""
    service = get_algo_trading_service(db)
    order = await service.create_iceberg_order(
        user_id="current_user",
        **data.model_dump()
    )
    return order


@router.get("", response_model=List[AlgoOrderResponse])
async def list_algo_orders(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取算法订单列表"""
    service = get_algo_trading_service(db)
    orders = await service.get_user_algo_orders(
        user_id="current_user",
        status=status
    )
    return orders


@router.get("/{algo_id}", response_model=AlgoOrderResponse)
async def get_algo_order(
    algo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取算法订单详情"""
    service = get_algo_trading_service(db)
    order = await service.get_algo_order(algo_id)
    if not order:
        raise HTTPException(status_code=404, detail="算法订单不存在")
    return order


@router.get("/{algo_id}/slices", response_model=List[AlgoSliceResponse])
async def get_algo_slices(
    algo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取算法订单切片"""
    service = get_algo_trading_service(db)
    slices = await service.get_order_slices(algo_id)
    return slices


@router.post("/{algo_id}/start", response_model=AlgoOrderResponse)
async def start_algo_order(
    algo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """启动算法订单"""
    service = get_algo_trading_service(db)
    try:
        order = await service.start_algo_order(algo_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{algo_id}/pause", response_model=AlgoOrderResponse)
async def pause_algo_order(
    algo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """暂停算法订单"""
    service = get_algo_trading_service(db)
    try:
        order = await service.pause_algo_order(algo_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{algo_id}/cancel", response_model=AlgoOrderResponse)
async def cancel_algo_order(
    algo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取消算法订单"""
    service = get_algo_trading_service(db)
    try:
        order = await service.cancel_algo_order(algo_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
