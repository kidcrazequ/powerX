"""
PowerX 组合订单 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.combo_order_service import get_combo_order_service

router = APIRouter(prefix="/combo-orders", tags=["组合订单"])


class ComboOrderItemCreate(BaseModel):
    province: str = "guangdong"
    market_type: str = "spot"
    order_type: str  # buy, sell
    quantity: float
    price: Optional[float] = None
    priority: int = 0


class ComboOrderCreate(BaseModel):
    name: str
    description: Optional[str] = None
    execution_strategy: str = "all_or_none"
    items: List[ComboOrderItemCreate]


class ComboOrderItemResponse(BaseModel):
    order_id: str
    province: str
    market_type: str
    order_type: str
    quantity: float
    price: Optional[float]
    status: str
    filled_quantity: float
    filled_price: Optional[float]
    priority: int

    class Config:
        from_attributes = True


class ComboOrderResponse(BaseModel):
    combo_id: str
    name: str
    description: Optional[str]
    execution_strategy: str
    status: str
    total_orders: int
    filled_orders: int
    total_quantity: float
    total_amount: float
    items: List[ComboOrderItemResponse]

    class Config:
        from_attributes = True


@router.post("", response_model=ComboOrderResponse)
async def create_combo_order(
    data: ComboOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建组合订单"""
    service = get_combo_order_service(db)
    
    items = [item.model_dump() for item in data.items]
    combo = await service.create_combo(
        user_id="current_user",  # TODO: 从认证获取
        name=data.name,
        items=items,
        execution_strategy=data.execution_strategy,
        description=data.description
    )
    
    return combo


@router.get("", response_model=List[ComboOrderResponse])
async def list_combo_orders(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取组合订单列表"""
    service = get_combo_order_service(db)
    combos = await service.get_user_combos(
        user_id="current_user",
        status=status
    )
    return combos


@router.get("/{combo_id}", response_model=ComboOrderResponse)
async def get_combo_order(
    combo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取组合订单详情"""
    service = get_combo_order_service(db)
    combo = await service.get_combo(combo_id)
    if not combo:
        raise HTTPException(status_code=404, detail="组合订单不存在")
    return combo


@router.post("/{combo_id}/submit", response_model=ComboOrderResponse)
async def submit_combo_order(
    combo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """提交组合订单"""
    service = get_combo_order_service(db)
    try:
        combo = await service.submit_combo(combo_id)
        return combo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{combo_id}/cancel", response_model=ComboOrderResponse)
async def cancel_combo_order(
    combo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取消组合订单"""
    service = get_combo_order_service(db)
    try:
        combo = await service.cancel_combo(combo_id)
        return combo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{combo_id}/items", response_model=ComboOrderItemResponse)
async def add_combo_item(
    combo_id: str,
    item: ComboOrderItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """添加子订单"""
    service = get_combo_order_service(db)
    try:
        new_item = await service.add_item(combo_id, item.model_dump())
        return new_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{combo_id}/items/{order_id}")
async def remove_combo_item(
    combo_id: str,
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """移除子订单"""
    service = get_combo_order_service(db)
    try:
        removed = await service.remove_item(combo_id, order_id)
        if not removed:
            raise HTTPException(status_code=404, detail="子订单不存在")
        return {"message": "已移除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
