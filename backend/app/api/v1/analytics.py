"""
PowerX 数据分析 API

创建日期: 2026-01-07
作者: zhi.qu

交易绩效、收益分析和趋势分析接口
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from loguru import logger

from app.api.deps import get_current_user, get_db
from app.services.analytics_service import AnalyticsService, analytics_service
from app.schemas.response import success_response

router = APIRouter()


@router.get("/performance")
async def get_trading_performance(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    province: Optional[str] = Query(None, description="省份"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取交易绩效分析
    
    分析交易胜率、收益、交易量等指标
    """
    logger.info(f"获取交易绩效: user={current_user}")
    
    user_id = getattr(current_user, "id", None) or str(current_user)
    
    result = await analytics_service.get_trading_performance(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        province=province
    )
    
    return success_response(data=result)


@router.get("/attribution")
async def get_profit_attribution(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取收益归因分析
    
    分解收益来源：价差、时机、交易量、策略等
    """
    logger.info(f"获取收益归因: user={current_user}")
    
    user_id = getattr(current_user, "id", None) or str(current_user)
    
    result = await analytics_service.get_profit_attribution(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return success_response(data=result)


@router.get("/trend/{province}")
async def get_trend_analysis(
    province: str,
    days: int = Query(30, ge=7, le=90, description="分析天数"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取趋势分析
    
    分析价格走势、均线、波动率等
    """
    logger.info(f"获取趋势分析: province={province}, days={days}")
    
    result = await analytics_service.get_trend_analysis(
        province=province,
        days=days
    )
    
    return success_response(data=result)


@router.get("/comparison")
async def get_comparison_analysis(
    provinces: str = Query(..., description="省份列表，逗号分隔"),
    metric: str = Query("price", description="对比指标"),
    days: int = Query(7, ge=1, le=30, description="分析天数"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取对比分析
    
    多省份价格、成交量等指标对比
    """
    province_list = [p.strip() for p in provinces.split(",")]
    logger.info(f"获取对比分析: provinces={province_list}")
    
    result = await analytics_service.get_comparison_analysis(
        provinces=province_list,
        metric=metric,
        days=days
    )
    
    return success_response(data=result)


@router.get("/hourly-pattern/{province}")
async def get_hourly_pattern(
    province: str,
    days: int = Query(7, ge=1, le=30, description="分析天数"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取小时模式分析
    
    分析24小时价格规律，识别高峰低谷时段
    """
    logger.info(f"获取小时模式: province={province}")
    
    result = await analytics_service.get_hourly_pattern(
        province=province,
        days=days
    )
    
    return success_response(data=result)


@router.get("/summary")
async def get_analytics_summary(
    province: Optional[str] = Query(None, description="省份"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取分析概览
    
    汇总关键分析指标
    """
    logger.info(f"获取分析概览: user={current_user}")
    
    user_id = getattr(current_user, "id", None) or str(current_user)
    
    # 获取各类分析数据
    performance = await analytics_service.get_trading_performance(user_id)
    attribution = await analytics_service.get_profit_attribution(user_id)
    
    summary = {
        "performance": {
            "win_rate": performance["summary"]["win_rate"],
            "total_profit": performance["summary"]["total_profit"],
            "total_trades": performance["summary"]["total_trades"]
        },
        "attribution": {
            "main_driver": max(
                attribution["attribution"].items(),
                key=lambda x: x[1]["percentage"]
            )[0],
            "excess_return": attribution["benchmark_comparison"]["excess_return"]
        },
        "risk_metrics": {
            "sharpe_ratio": attribution["risk_adjusted_metrics"]["sharpe_ratio"],
            "max_drawdown": attribution["risk_adjusted_metrics"]["max_drawdown"]
        }
    }
    
    return success_response(data=summary)
