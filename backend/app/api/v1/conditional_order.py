"""
PowerX 条件单 API

创建日期: 2026-01-07
作者: zhi.qu

提供条件单相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.conditional_order_service import ConditionalOrderService
from app.models.conditional_order import ConditionalOrder, ConditionType, ConditionStatus
from app.schemas.response import APIResponse


router = APIRouter()


# ============ 请求/响应模型 ============

class ConditionalOrderCreate(BaseModel):
    """创建条件单请求"""
    name: Optional[str] = Field(None, description="条件单名称", max_length=200)
    condition_type: str = Field(..., description="条件类型")
    province: str = Field(..., description="省份")
    market_type: str = Field("DAY_AHEAD", description="市场类型")
    
    # 触发条件
    trigger_price: Optional[float] = Field(None, description="触发价格")
    trigger_change_pct: Optional[float] = Field(None, description="触发变动百分比")
    trigger_time: Optional[datetime] = Field(None, description="触发时间")
    trigger_volume: Optional[float] = Field(None, description="触发交易量")
    condition_params: Optional[Dict[str, Any]] = Field(None, description="其他条件参数")
    
    # 目标订单
    order_direction: str = Field(..., description="订单方向 (BUY/SELL)")
    order_quantity: float = Field(..., gt=0, description="交易数量 (MWh)")
    order_price_type: str = Field("MARKET", description="订单价格类型")
    order_limit_price: Optional[float] = Field(None, description="限价单价格")
    
    # 有效期
    valid_until: Optional[datetime] = Field(None, description="有效期截止时间")


class ConditionalOrderResponse(BaseModel):
    """条件单响应"""
    id: int
    user_id: str
    name: Optional[str]
    condition_type: str
    province: str
    market_type: str
    trigger_price: Optional[float]
    trigger_change_pct: Optional[float]
    trigger_time: Optional[str]
    trigger_volume: Optional[float]
    order_direction: str
    order_quantity: float
    order_price_type: str
    order_limit_price: Optional[float]
    status: str
    is_enabled: bool
    valid_from: str
    valid_until: Optional[str]
    triggered_at: Optional[str]
    triggered_price: Optional[float]
    executed_at: Optional[str]
    executed_order_id: Optional[str]
    created_at: str


class TriggerLogResponse(BaseModel):
    """触发日志响应"""
    id: int
    conditional_order_id: int
    trigger_time: str
    trigger_reason: Optional[str]
    market_price: Optional[float]
    success: bool
    order_id: Optional[str]
    error_message: Optional[str]


# ============ API 端点 ============

@router.post("", response_model=APIResponse[ConditionalOrderResponse])
async def create_conditional_order(
    request: ConditionalOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建条件单
    
    支持多种触发条件：价格高于/低于、价格变动百分比、时间触发、成交量触发
    """
    service = ConditionalOrderService(db)
    
    try:
        order = await service.create_order(
            user_id=current_user.id,
            name=request.name,
            condition_type=request.condition_type,
            province=request.province,
            market_type=request.market_type,
            trigger_price=request.trigger_price,
            trigger_change_pct=request.trigger_change_pct,
            trigger_time=request.trigger_time,
            trigger_volume=request.trigger_volume,
            condition_params=request.condition_params,
            order_direction=request.order_direction,
            order_quantity=request.order_quantity,
            order_price_type=request.order_price_type,
            order_limit_price=request.order_limit_price,
            valid_until=request.valid_until
        )
        
        return APIResponse.success_response(
            _order_to_response(order),
            message="条件单创建成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=APIResponse[List[ConditionalOrderResponse]])
async def get_conditional_orders(
    status_filter: Optional[str] = Query(None, alias="status", description="状态过滤"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户的条件单列表
    """
    service = ConditionalOrderService(db)
    orders = await service.get_user_orders(
        user_id=current_user.id,
        status=status_filter,
        limit=limit
    )
    
    return APIResponse.success_response([
        _order_to_response(order) for order in orders
    ])


@router.get("/types", response_model=APIResponse[List[Dict[str, str]]])
async def get_condition_types(
    current_user = Depends(get_current_user)
):
    """
    获取支持的条件类型列表
    """
    types = [
        {"value": ConditionType.PRICE_ABOVE.value, "label": "价格高于", "description": "当市场价格高于指定值时触发"},
        {"value": ConditionType.PRICE_BELOW.value, "label": "价格低于", "description": "当市场价格低于指定值时触发"},
        {"value": ConditionType.PRICE_CHANGE_PCT.value, "label": "价格变动", "description": "当价格变动超过指定百分比时触发"},
        {"value": ConditionType.TIME_TRIGGER.value, "label": "定时触发", "description": "在指定时间自动触发"},
        {"value": ConditionType.VOLUME_ABOVE.value, "label": "成交量高于", "description": "当成交量超过指定值时触发"},
        {"value": ConditionType.INDICATOR.value, "label": "技术指标", "description": "当技术指标满足条件时触发"},
    ]
    return APIResponse.success_response(types)


@router.get("/{order_id}", response_model=APIResponse[ConditionalOrderResponse])
async def get_conditional_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取条件单详情
    """
    service = ConditionalOrderService(db)
    order = await service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="条件单不存在"
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此条件单"
        )
    
    return APIResponse.success_response(_order_to_response(order))


@router.delete("/{order_id}", response_model=APIResponse[bool])
async def cancel_conditional_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    取消条件单
    """
    service = ConditionalOrderService(db)
    
    try:
        success = await service.cancel_order(order_id, current_user.id)
        if success:
            return APIResponse.success_response(True, message="条件单已取消")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="条件单不存在"
            )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{order_id}/logs", response_model=APIResponse[List[TriggerLogResponse]])
async def get_trigger_logs(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取条件单的触发日志
    """
    service = ConditionalOrderService(db)
    
    # 验证权限
    order = await service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="条件单不存在"
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此条件单"
        )
    
    logs = await service.get_trigger_logs(order_id)
    
    return APIResponse.success_response([
        TriggerLogResponse(
            id=log.id,
            conditional_order_id=log.conditional_order_id,
            trigger_time=log.trigger_time.isoformat() if log.trigger_time else "",
            trigger_reason=log.trigger_reason,
            market_price=log.market_price,
            success=log.success,
            order_id=log.order_id,
            error_message=log.error_message
        )
        for log in logs
    ])


# ============ 辅助函数 ============

def _order_to_response(order: ConditionalOrder) -> ConditionalOrderResponse:
    """将条件单模型转换为响应"""
    return ConditionalOrderResponse(
        id=order.id,
        user_id=order.user_id,
        name=order.name,
        condition_type=order.condition_type,
        province=order.province,
        market_type=order.market_type,
        trigger_price=order.trigger_price,
        trigger_change_pct=order.trigger_change_pct,
        trigger_time=order.trigger_time.isoformat() if order.trigger_time else None,
        trigger_volume=order.trigger_volume,
        order_direction=order.order_direction,
        order_quantity=order.order_quantity,
        order_price_type=order.order_price_type,
        order_limit_price=order.order_limit_price,
        status=order.status,
        is_enabled=order.is_enabled,
        valid_from=order.valid_from.isoformat() if order.valid_from else "",
        valid_until=order.valid_until.isoformat() if order.valid_until else None,
        triggered_at=order.triggered_at.isoformat() if order.triggered_at else None,
        triggered_price=order.triggered_price,
        executed_at=order.executed_at.isoformat() if order.executed_at else None,
        executed_order_id=order.executed_order_id,
        created_at=order.created_at.isoformat() if order.created_at else ""
    )
