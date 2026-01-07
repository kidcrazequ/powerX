"""
PowerX 系统健康 API

创建日期: 2026-01-07
作者: zhi.qu

提供系统健康检查和 API 统计相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from app.api.deps import get_db, get_current_user
from app.services.health_service import health_service
from app.schemas.response import APIResponse


router = APIRouter()


@router.get("/status", response_model=APIResponse[Dict[str, Any]])
async def get_system_status(
    current_user = Depends(get_current_user)
):
    """
    获取系统状态
    
    返回 CPU、内存、磁盘使用情况和运行时间
    """
    status = await health_service.get_system_status()
    return APIResponse.success_response(status)


@router.get("/database", response_model=APIResponse[Dict[str, Any]])
async def get_database_status(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取数据库状态
    
    检查数据库连接和响应延迟
    """
    status = await health_service.get_db_status(db)
    return APIResponse.success_response(status)


@router.get("/api-metrics", response_model=APIResponse[Dict[str, Any]])
async def get_api_metrics(
    hours: int = Query(24, ge=1, le=168, description="统计时间范围(小时)"),
    current_user = Depends(get_current_user)
):
    """
    获取 API 调用统计
    
    返回调用次数、平均响应时间、错误率等指标
    """
    metrics = health_service.get_api_metrics(hours=hours)
    return APIResponse.success_response(metrics)


@router.get("/api-timeline", response_model=APIResponse[List[Dict[str, Any]]])
async def get_api_timeline(
    hours: int = Query(24, ge=1, le=168, description="统计时间范围(小时)"),
    interval: int = Query(60, ge=5, le=1440, description="时间间隔(分钟)"),
    current_user = Depends(get_current_user)
):
    """
    获取 API 调用时间线
    
    返回按时间间隔聚合的调用统计数据
    """
    timeline = health_service.get_api_timeline(hours=hours, interval_minutes=interval)
    return APIResponse.success_response(timeline)


@router.get("/report", response_model=APIResponse[Dict[str, Any]])
async def get_health_report(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取完整健康报告
    
    返回系统、数据库、API 的综合健康评估
    """
    report = await health_service.get_full_health_report(db)
    return APIResponse.success_response(report)


@router.get("/ping")
async def ping():
    """
    简单的健康检查端点
    
    用于负载均衡器或监控系统的健康检查
    """
    return {"status": "ok", "message": "pong"}
