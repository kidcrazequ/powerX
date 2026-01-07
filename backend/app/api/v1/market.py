"""
PowerX 市场数据 API

创建日期: 2026-01-07
作者: zhi.qu

市场数据相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.services.market_service import MarketService
from app.api.deps import get_current_user

router = APIRouter()


class PriceDataResponse(BaseModel):
    """价格数据响应"""
    province: str
    date: str
    hour: int
    day_ahead_price: float
    realtime_price: Optional[float] = None
    volume_mwh: Optional[float] = None


class MarketSummaryResponse(BaseModel):
    """市场概览响应"""
    province: str
    avg_price: float
    max_price: float
    min_price: float
    total_volume: float
    price_change_percent: float


class HourlyPricesResponse(BaseModel):
    """24小时价格响应"""
    province: str
    date: str
    prices: List[float]


@router.get("/summary/{province}", response_model=MarketSummaryResponse)
async def get_market_summary(
    province: str,
    current_user = Depends(get_current_user)
):
    """
    获取指定省份市场概览
    
    - **province**: 省份名称（广东、浙江、山东等）
    """
    service = MarketService()
    summary = await service.get_market_summary(province)
    
    if not summary:
        raise HTTPException(status_code=404, detail=f"未找到 {province} 省市场数据")
    
    return summary


@router.get("/prices/{province}", response_model=List[PriceDataResponse])
async def get_market_prices(
    province: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user = Depends(get_current_user)
):
    """
    获取指定省份历史价格数据
    
    - **province**: 省份名称
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    service = MarketService()
    prices = await service.get_historical_prices(province, start_date, end_date)
    return prices


@router.get("/hourly/{province}", response_model=HourlyPricesResponse)
async def get_hourly_prices(
    province: str,
    target_date: Optional[date] = None,
    current_user = Depends(get_current_user)
):
    """
    获取指定省份24小时价格曲线
    
    - **province**: 省份名称
    - **target_date**: 目标日期，默认为今天
    """
    service = MarketService()
    hourly = await service.get_hourly_prices(province, target_date)
    return hourly


@router.get("/comparison")
async def get_price_comparison(
    provinces: str = Query(..., description="省份列表，用逗号分隔"),
    target_date: Optional[date] = None,
    current_user = Depends(get_current_user)
):
    """
    获取多省份价格对比
    
    - **provinces**: 省份列表，如 "广东,浙江,山东"
    - **target_date**: 目标日期
    """
    province_list = [p.strip() for p in provinces.split(",")]
    service = MarketService()
    
    result = {}
    for province in province_list:
        hourly = await service.get_hourly_prices(province, target_date)
        result[province] = hourly
    
    return result


@router.get("/realtime/{province}")
async def get_realtime_price(
    province: str,
    current_user = Depends(get_current_user)
):
    """
    获取实时电价（模拟）
    
    - **province**: 省份名称
    """
    service = MarketService()
    realtime = await service.get_realtime_price(province)
    return {
        "province": province,
        "price": realtime["price"],
        "timestamp": datetime.now().isoformat(),
        "change_percent": realtime["change_percent"]
    }


@router.get("/provinces")
async def get_supported_provinces(
    current_user = Depends(get_current_user)
):
    """
    获取支持的省份列表
    """
    service = MarketService()
    provinces = service.get_supported_provinces()
    return {"provinces": provinces}
