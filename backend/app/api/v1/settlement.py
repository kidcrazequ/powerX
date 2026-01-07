"""
PowerX 结算 API

创建日期: 2026-01-07
作者: zhi.qu

结算相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from enum import Enum

from app.services.settlement_service import SettlementService
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# ============ 枚举类型 ============

class SettlementType(str, Enum):
    DAY_AHEAD = "DAY_AHEAD"
    INTRADAY = "INTRADAY"
    MID_LONG = "MID_LONG"


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    SETTLED = "SETTLED"
    DISPUTED = "DISPUTED"


# ============ 请求/响应模型 ============

class SettlementRecordResponse(BaseModel):
    """结算记录响应"""
    id: str
    date: str
    settlement_type: str
    quantity_mwh: float
    avg_price: float
    amount: float
    fee: float
    net_amount: float
    status: str


class SettlementSummaryResponse(BaseModel):
    """结算汇总响应"""
    period: str
    total_quantity_mwh: float
    total_amount: float
    total_fee: float
    net_amount: float
    spot_quantity_mwh: float
    mid_long_quantity_mwh: float
    avg_spot_price: float
    avg_mid_long_price: float


class FeeBreakdownResponse(BaseModel):
    """费用明细响应"""
    mid_long_cost: float
    spot_cost: float
    transmission_fee: float
    service_fee: float
    other_fee: float
    total: float


# ============ API 端点 ============

@router.get("/records", response_model=List[SettlementRecordResponse])
async def get_settlement_records(
    settlement_type: Optional[SettlementType] = None,
    status: Optional[SettlementStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取结算记录列表
    """
    service = SettlementService(db)
    
    records = await service.get_records(
        user_id=current_user.id,
        settlement_type=settlement_type.value if settlement_type else None,
        status=status.value if status else None,
        start_date=start_date,
        end_date=end_date
    )
    
    return [
        SettlementRecordResponse(
            id=r["id"],
            date=r["date"],
            settlement_type=r["settlement_type"],
            quantity_mwh=r["quantity_mwh"],
            avg_price=r["avg_price"],
            amount=r["amount"],
            fee=r["fee"],
            net_amount=r["net_amount"],
            status=r["status"]
        )
        for r in records
    ]


@router.get("/records/{record_id}", response_model=SettlementRecordResponse)
async def get_settlement_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取结算记录详情
    """
    service = SettlementService(db)
    record = await service.get_record(record_id, current_user.id)
    
    if not record:
        raise HTTPException(status_code=404, detail="结算记录不存在")
    
    return SettlementRecordResponse(
        id=record["id"],
        date=record["date"],
        settlement_type=record["settlement_type"],
        quantity_mwh=record["quantity_mwh"],
        avg_price=record["avg_price"],
        amount=record["amount"],
        fee=record["fee"],
        net_amount=record["net_amount"],
        status=record["status"]
    )


@router.get("/summary/monthly", response_model=SettlementSummaryResponse)
async def get_monthly_summary(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取月度结算汇总
    """
    service = SettlementService(db)
    
    summary = await service.get_monthly_summary(
        user_id=current_user.id,
        year=year,
        month=month
    )
    
    return SettlementSummaryResponse(
        period=f"{year}年{month}月",
        total_quantity_mwh=summary["total_quantity_mwh"],
        total_amount=summary["total_amount"],
        total_fee=summary["total_fee"],
        net_amount=summary["net_amount"],
        spot_quantity_mwh=summary["spot_quantity_mwh"],
        mid_long_quantity_mwh=summary["mid_long_quantity_mwh"],
        avg_spot_price=summary["avg_spot_price"],
        avg_mid_long_price=summary["avg_mid_long_price"]
    )


@router.get("/fee-breakdown", response_model=FeeBreakdownResponse)
async def get_fee_breakdown(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取费用构成明细
    """
    service = SettlementService(db)
    
    breakdown = await service.get_fee_breakdown(
        user_id=current_user.id,
        year=year,
        month=month
    )
    
    return FeeBreakdownResponse(
        mid_long_cost=breakdown["mid_long_cost"],
        spot_cost=breakdown["spot_cost"],
        transmission_fee=breakdown["transmission_fee"],
        service_fee=breakdown["service_fee"],
        other_fee=breakdown["other_fee"],
        total=breakdown["total"]
    )


@router.get("/daily-trend")
async def get_daily_trend(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取日结算趋势
    """
    service = SettlementService(db)
    
    trend = await service.get_daily_trend(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return trend


@router.post("/export")
async def export_settlement_report(
    year: int,
    month: int,
    format: str = "pdf",
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    导出结算报表
    """
    # 这里返回模拟响应，实际应生成文件
    return {
        "message": "报表生成中",
        "download_url": f"/api/v1/settlement/download/{year}-{month}.{format}"
    }
