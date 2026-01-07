"""
PowerX 历史回放 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any

from app.api.deps import get_current_user
from app.services.history_replay_service import get_history_replay_service
from app.schemas.response import APIResponse

router = APIRouter()


@router.get("/dates", response_model=APIResponse[List[str]])
async def get_available_dates(
    data_type: str = Query("market", description="数据类型"),
    current_user = Depends(get_current_user)
):
    """获取可回放的日期列表"""
    service = get_history_replay_service()
    dates = await service.get_available_dates(data_type)
    return APIResponse.success_response(dates)


@router.get("/data/{date}", response_model=APIResponse[List[Dict[str, Any]]])
async def get_replay_data(
    date: str,
    data_type: str = Query("market", description="数据类型"),
    start_time: str = Query("09:00", description="开始时间"),
    end_time: str = Query("16:00", description="结束时间"),
    interval: int = Query(5, description="时间间隔(分钟)"),
    current_user = Depends(get_current_user)
):
    """获取指定日期的回放数据"""
    service = get_history_replay_service()
    data = await service.get_replay_data(date, data_type, start_time, end_time, interval)
    return APIResponse.success_response(data)


@router.get("/events/{date}", response_model=APIResponse[List[Dict[str, Any]]])
async def get_trading_events(
    date: str,
    current_user = Depends(get_current_user)
):
    """获取指定日期的交易事件"""
    service = get_history_replay_service()
    events = await service.get_trading_events(date)
    return APIResponse.success_response(events)


@router.get("/summary/{date}", response_model=APIResponse[Dict[str, Any]])
async def get_summary(
    date: str,
    current_user = Depends(get_current_user)
):
    """获取日期汇总数据"""
    service = get_history_replay_service()
    summary = await service.get_summary(date)
    return APIResponse.success_response(summary)
