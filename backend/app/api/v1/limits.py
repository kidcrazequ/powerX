"""
PowerX 交易限额 API

创建日期: 2026-01-07
作者: zhi.qu

提供交易限额管理相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.limit_service import LimitService, LimitCheckResult
from app.models.trading_limit import TradingLimit, LimitViolation, LimitType
from app.schemas.response import APIResponse


router = APIRouter()


# ============ 请求/响应模型 ============

class LimitCreate(BaseModel):
    """创建限额请求"""
    limit_type: str = Field(..., description="限额类型")
    limit_value: float = Field(..., gt=0, description="限额值")
    user_id: Optional[str] = Field(None, description="用户ID（null表示全局）")
    province: Optional[str] = Field(None, description="适用省份")
    market_type: Optional[str] = Field(None, description="适用市场类型")
    direction: Optional[str] = Field(None, description="适用方向 (BUY/SELL)")
    name: Optional[str] = Field(None, description="限额名称")
    description: Optional[str] = Field(None, description="描述")


class LimitUpdate(BaseModel):
    """更新限额请求"""
    limit_value: Optional[float] = Field(None, gt=0)
    is_enabled: Optional[bool] = None


class LimitCheckRequest(BaseModel):
    """限额检查请求"""
    direction: str = Field(..., description="交易方向 (BUY/SELL)")
    quantity: float = Field(..., gt=0, description="交易数量")
    price: float = Field(..., gt=0, description="交易价格")
    province: Optional[str] = Field(None, description="省份")
    market_type: Optional[str] = Field(None, description="市场类型")


class LimitResponse(BaseModel):
    """限额响应"""
    id: int
    user_id: Optional[str]
    limit_type: str
    limit_value: float
    province: Optional[str]
    market_type: Optional[str]
    direction: Optional[str]
    is_enabled: bool
    name: Optional[str]
    description: Optional[str]
    created_at: str


class ViolationResponse(BaseModel):
    """违规响应"""
    id: int
    user_id: str
    limit_id: int
    violation_time: str
    attempted_value: float
    limit_value: float
    current_usage: Optional[float]
    is_resolved: bool
    resolution_note: Optional[str]


# ============ API 端点 ============

@router.post("", response_model=APIResponse[LimitResponse])
async def create_limit(
    request: LimitCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建交易限额
    
    支持的限额类型：
    - DAILY_AMOUNT: 每日交易金额
    - DAILY_QUANTITY: 每日交易数量
    - SINGLE_AMOUNT: 单笔交易金额
    - SINGLE_QUANTITY: 单笔交易数量
    - POSITION: 持仓限额
    """
    service = LimitService(db)
    
    limit = await service.create_limit(
        limit_type=request.limit_type,
        limit_value=request.limit_value,
        user_id=request.user_id,
        province=request.province,
        market_type=request.market_type,
        direction=request.direction,
        name=request.name,
        description=request.description,
        created_by=current_user.id
    )
    
    return APIResponse.success_response(
        _limit_to_response(limit),
        message="限额创建成功"
    )


@router.get("", response_model=APIResponse[List[LimitResponse]])
async def get_limits(
    user_id: Optional[str] = Query(None, description="用户ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取限额配置列表
    """
    service = LimitService(db)
    limits = await service.get_all_limits(user_id=user_id)
    
    return APIResponse.success_response([
        _limit_to_response(limit) for limit in limits
    ])


@router.get("/types", response_model=APIResponse[List[Dict[str, str]]])
async def get_limit_types(
    current_user = Depends(get_current_user)
):
    """
    获取支持的限额类型
    """
    types = [
        {"value": LimitType.DAILY_AMOUNT.value, "label": "每日交易金额", "unit": "元"},
        {"value": LimitType.DAILY_QUANTITY.value, "label": "每日交易数量", "unit": "MWh"},
        {"value": LimitType.SINGLE_AMOUNT.value, "label": "单笔交易金额", "unit": "元"},
        {"value": LimitType.SINGLE_QUANTITY.value, "label": "单笔交易数量", "unit": "MWh"},
        {"value": LimitType.POSITION.value, "label": "持仓限额", "unit": "MWh"},
    ]
    return APIResponse.success_response(types)


@router.post("/check", response_model=APIResponse[Dict[str, Any]])
async def check_limit(
    request: LimitCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    检查交易是否超过限额
    
    在下单前调用此接口检查是否满足限额要求
    """
    service = LimitService(db)
    
    result = await service.check_limit(
        user_id=current_user.id,
        direction=request.direction,
        quantity=request.quantity,
        price=request.price,
        province=request.province,
        market_type=request.market_type
    )
    
    return APIResponse.success_response(result.to_dict())


@router.put("/{limit_id}", response_model=APIResponse[LimitResponse])
async def update_limit(
    limit_id: int,
    request: LimitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新限额配置
    """
    service = LimitService(db)
    
    limit = await service.update_limit(
        limit_id=limit_id,
        limit_value=request.limit_value,
        is_enabled=request.is_enabled
    )
    
    if not limit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="限额配置不存在"
        )
    
    return APIResponse.success_response(
        _limit_to_response(limit),
        message="限额更新成功"
    )


@router.delete("/{limit_id}", response_model=APIResponse[bool])
async def delete_limit(
    limit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    删除限额配置
    """
    service = LimitService(db)
    success = await service.delete_limit(limit_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="限额配置不存在"
        )
    
    return APIResponse.success_response(True, message="限额已删除")


@router.get("/violations", response_model=APIResponse[List[ViolationResponse]])
async def get_violations(
    include_resolved: bool = Query(False, description="是否包含已处理的违规"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取违规记录
    """
    service = LimitService(db)
    violations = await service.get_violations(
        user_id=current_user.id,
        limit=limit,
        include_resolved=include_resolved
    )
    
    return APIResponse.success_response([
        ViolationResponse(
            id=v.id,
            user_id=v.user_id,
            limit_id=v.limit_id,
            violation_time=v.violation_time.isoformat() if v.violation_time else "",
            attempted_value=v.attempted_value,
            limit_value=v.limit_value,
            current_usage=v.current_usage,
            is_resolved=v.is_resolved,
            resolution_note=v.resolution_note
        )
        for v in violations
    ])


@router.post("/violations/{violation_id}/resolve", response_model=APIResponse[bool])
async def resolve_violation(
    violation_id: int,
    resolution_note: str = Query(..., description="处理说明"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    处理违规记录
    """
    service = LimitService(db)
    success = await service.resolve_violation(
        violation_id=violation_id,
        resolution_note=resolution_note,
        resolved_by=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="违规记录不存在"
        )
    
    return APIResponse.success_response(True, message="违规已处理")


@router.get("/usage/today", response_model=APIResponse[Dict[str, Any]])
async def get_today_usage(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取今日使用量
    """
    service = LimitService(db)
    usage = await service.get_daily_usage(current_user.id)
    
    if not usage:
        return APIResponse.success_response({
            "date": str(datetime.now().date()),
            "total_buy_quantity": 0,
            "total_sell_quantity": 0,
            "total_buy_amount": 0,
            "total_sell_amount": 0,
            "trade_count": 0
        })
    
    return APIResponse.success_response({
        "date": usage.date,
        "total_buy_quantity": usage.total_buy_quantity,
        "total_sell_quantity": usage.total_sell_quantity,
        "total_buy_amount": usage.total_buy_amount,
        "total_sell_amount": usage.total_sell_amount,
        "trade_count": usage.trade_count,
        "by_province": usage.by_province
    })


# ============ 辅助函数 ============

def _limit_to_response(limit: TradingLimit) -> LimitResponse:
    return LimitResponse(
        id=limit.id,
        user_id=limit.user_id,
        limit_type=limit.limit_type,
        limit_value=limit.limit_value,
        province=limit.province,
        market_type=limit.market_type,
        direction=limit.direction,
        is_enabled=limit.is_enabled,
        name=limit.name,
        description=limit.description,
        created_at=limit.created_at.isoformat() if limit.created_at else ""
    )


# 导入 datetime
from datetime import datetime
