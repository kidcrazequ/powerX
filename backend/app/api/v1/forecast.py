"""
PowerX 电量预测 API

创建日期: 2026-01-07
作者: zhi.qu

提供电量预测相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import date
from pydantic import BaseModel
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.services.forecast_service import ForecastService
from app.schemas.response import APIResponse


router = APIRouter()


# ============ 响应模型 ============

class HourlyData(BaseModel):
    """小时数据"""
    hour: int
    time: str
    load: int
    energy: float
    load_factor: float


class DailyLoadCurveStatistics(BaseModel):
    """日负荷曲线统计"""
    total_energy: float
    peak_load: int
    valley_load: int
    average_load: int
    peak_valley_ratio: float
    peak_hour: int
    valley_hour: int


class DailyLoadCurveResponse(BaseModel):
    """日负荷曲线响应"""
    province: str
    date: str
    hourly_data: List[HourlyData]
    statistics: DailyLoadCurveStatistics


class DailyForecastData(BaseModel):
    """每日预测数据"""
    date: str
    weekday: int
    weekday_name: str
    energy: float
    factor: float


class WeeklyForecastStatistics(BaseModel):
    """周预测统计"""
    total_energy: float
    average_energy: float
    max_energy: float
    min_energy: float


class WeeklyForecastResponse(BaseModel):
    """周电量预测响应"""
    province: str
    start_date: str
    end_date: str
    daily_data: List[DailyForecastData]
    statistics: WeeklyForecastStatistics


class MonthlyDailyData(BaseModel):
    """月度每日数据"""
    date: str
    day: int
    weekday: int
    energy: float


class MonthlyForecastStatistics(BaseModel):
    """月预测统计"""
    total_energy: float
    average_energy: float
    max_energy: float
    min_energy: float
    seasonal_factor: float


class MonthlyForecastResponse(BaseModel):
    """月电量预测响应"""
    province: str
    year: int
    month: int
    days_in_month: int
    daily_data: List[MonthlyDailyData]
    statistics: MonthlyForecastStatistics


class PeriodAnalysis(BaseModel):
    """时段分析"""
    hours: List[int]
    avg_load: int
    energy: float
    percentage: float


class PeakPeriodAnalysis(PeriodAnalysis):
    """峰时段分析"""
    max_load: int


class ValleyPeriodAnalysis(PeriodAnalysis):
    """谷时段分析"""
    min_load: int


class PeakValleyAnalysisResponse(BaseModel):
    """峰谷分析响应"""
    province: str
    date: str
    peak: PeakPeriodAnalysis
    valley: ValleyPeriodAnalysis
    flat: PeriodAnalysis
    recommendations: List[str]


# ============ API 端点 ============

@router.get("/daily", response_model=APIResponse[DailyLoadCurveResponse])
async def get_daily_load_curve(
    province: str = Query(..., description="省份代码 (例如: guangdong, zhejiang)"),
    target_date: date = Query(..., description="目标日期"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取日负荷曲线预测
    
    返回指定省份和日期的24小时负荷曲线数据
    """
    forecast_service = ForecastService(db)
    result = await forecast_service.get_daily_load_curve(
        province=province,
        target_date=target_date
    )
    return APIResponse.success_response(result)


@router.get("/weekly", response_model=APIResponse[WeeklyForecastResponse])
async def get_weekly_forecast(
    province: str = Query(..., description="省份代码"),
    start_date: date = Query(..., description="起始日期"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取周电量预测
    
    返回从指定日期开始的7天电量预测
    """
    forecast_service = ForecastService(db)
    result = await forecast_service.get_weekly_forecast(
        province=province,
        start_date=start_date
    )
    return APIResponse.success_response(result)


@router.get("/monthly", response_model=APIResponse[MonthlyForecastResponse])
async def get_monthly_forecast(
    province: str = Query(..., description="省份代码"),
    year: int = Query(..., description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份 (1-12)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取月电量预测
    
    返回指定年月的每日电量预测
    """
    forecast_service = ForecastService(db)
    result = await forecast_service.get_monthly_forecast(
        province=province,
        year=year,
        month=month
    )
    return APIResponse.success_response(result)


@router.get("/peak-valley", response_model=APIResponse[PeakValleyAnalysisResponse])
async def get_peak_valley_analysis(
    province: str = Query(..., description="省份代码"),
    target_date: date = Query(..., description="目标日期"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取峰谷时段分析
    
    返回峰谷平时段的电量分布和交易建议
    """
    forecast_service = ForecastService(db)
    result = await forecast_service.get_peak_valley_analysis(
        province=province,
        target_date=target_date
    )
    return APIResponse.success_response(result)
