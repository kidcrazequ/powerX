"""
PowerX AI 顾问 API

创建日期: 2026-01-07
作者: zhi.qu

提供 AI 交易建议和异常检测相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.ai_advisor_service import AIAdvisorService, ai_advisor_service
from app.services.anomaly_detection_service import AnomalyDetectionService, anomaly_detection_service
from app.schemas.response import APIResponse


router = APIRouter()


# ============ 响应模型 ============

class RecommendationResponse(BaseModel):
    """交易建议响应"""
    id: str
    province: str
    market_type: str
    direction: str
    confidence: float
    current_price: float
    target_price: float
    potential_profit_pct: float
    reason: str
    factors: List[Dict[str, Any]]
    risk_level: str
    created_at: str
    valid_until: str


class MarketAnalysisResponse(BaseModel):
    """市场分析响应"""
    province: str
    market_type: str
    analysis_time: str
    current_price: float
    price_trend: str
    volatility: float
    sentiment: str
    sentiment_score: float
    price_predictions: List[Dict[str, Any]]
    key_factors: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]


class OpportunityScoreResponse(BaseModel):
    """机会评分响应"""
    province: str
    market_type: str
    opportunity_score: int
    score_breakdown: Dict[str, float]
    recommendation: str


class AnomalyResponse(BaseModel):
    """异常响应"""
    id: str
    type: str
    severity: str
    province: str
    market_type: str
    detected_at: str
    description: str
    current_value: float
    expected_value: float
    deviation_pct: float
    details: Dict[str, Any]
    recommendations: List[str]


class DetectionRequest(BaseModel):
    """异常检测请求"""
    province: str = Field(..., description="省份")
    market_type: str = Field("DAY_AHEAD", description="市场类型")
    current_price: Optional[float] = Field(None, description="当前价格")
    current_volume: Optional[float] = Field(None, description="当前成交量")
    historical_prices: Optional[List[float]] = Field(None, description="历史价格")
    historical_volumes: Optional[List[float]] = Field(None, description="历史成交量")


# ============ API 端点 ============

@router.get("/recommendations", response_model=APIResponse[List[RecommendationResponse]])
async def get_recommendations(
    provinces: Optional[str] = Query(None, description="省份列表，逗号分隔"),
    market_type: str = Query("DAY_AHEAD", description="市场类型"),
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取 AI 交易建议
    
    返回基于市场分析的智能交易建议，包括买入/卖出/持有信号、置信度、目标价格等
    """
    province_list = provinces.split(",") if provinces else None
    
    service = AIAdvisorService(db)
    recommendations = await service.generate_recommendations(
        provinces=province_list,
        market_type=market_type,
        limit=limit
    )
    
    return APIResponse.success_response([
        RecommendationResponse(**rec.to_dict())
        for rec in recommendations
    ])


@router.get("/market-analysis", response_model=APIResponse[MarketAnalysisResponse])
async def get_market_analysis(
    province: str = Query(..., description="省份"),
    market_type: str = Query("DAY_AHEAD", description="市场类型"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取市场分析
    
    返回详细的市场分析报告，包括价格趋势、波动率、市场情绪、价格预测等
    """
    service = AIAdvisorService(db)
    analysis = await service.analyze_market(province, market_type)
    
    return APIResponse.success_response(MarketAnalysisResponse(**analysis))


@router.get("/opportunity-scores", response_model=APIResponse[List[OpportunityScoreResponse]])
async def get_opportunity_scores(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取所有省份的交易机会评分
    
    返回 0-100 分的机会评分，帮助快速判断哪些市场值得关注
    """
    service = AIAdvisorService(db)
    opportunities = await service.get_all_opportunities()
    
    return APIResponse.success_response([
        OpportunityScoreResponse(
            province=opp["province"],
            market_type=opp["market_type"],
            opportunity_score=opp["opportunity_score"],
            score_breakdown=opp["score_breakdown"],
            recommendation=opp["recommendation"]
        )
        for opp in opportunities
    ])


@router.get("/opportunity-score/{province}", response_model=APIResponse[Dict[str, Any]])
async def get_province_opportunity_score(
    province: str,
    market_type: str = Query("DAY_AHEAD", description="市场类型"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取指定省份的交易机会评分详情
    """
    service = AIAdvisorService(db)
    score = await service.get_opportunity_score(province, market_type)
    
    return APIResponse.success_response(score)


# ============ 异常检测 API ============

@router.post("/anomaly-detection", response_model=APIResponse[List[AnomalyResponse]])
async def run_anomaly_detection(
    request: DetectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    运行异常检测
    
    对提供的市场数据进行异常检测，包括价格异常、成交量异常和交易模式异常
    """
    service = AnomalyDetectionService(db)
    
    market_data = {
        "market_type": request.market_type,
    }
    
    if request.current_price is not None:
        market_data["current_price"] = request.current_price
    if request.historical_prices:
        market_data["historical_prices"] = request.historical_prices
    if request.current_volume is not None:
        market_data["current_volume"] = request.current_volume
    if request.historical_volumes:
        market_data["historical_volumes"] = request.historical_volumes
    
    anomalies = await service.run_full_detection(request.province, market_data)
    
    return APIResponse.success_response([
        AnomalyResponse(**a.to_dict())
        for a in anomalies
    ])


@router.get("/anomalies", response_model=APIResponse[List[AnomalyResponse]])
async def get_recent_anomalies(
    hours: int = Query(24, ge=1, le=168, description="查询时间范围(小时)"),
    severity: Optional[str] = Query(None, description="严重程度过滤 (LOW/MEDIUM/HIGH/CRITICAL)"),
    province: Optional[str] = Query(None, description="省份过滤"),
    current_user = Depends(get_current_user)
):
    """
    获取最近的异常记录
    """
    anomalies = await anomaly_detection_service.get_recent_anomalies(
        hours=hours,
        severity=severity,
        province=province
    )
    
    return APIResponse.success_response([
        AnomalyResponse(**a.to_dict())
        for a in anomalies
    ])


@router.get("/anomaly-stats", response_model=APIResponse[Dict[str, Any]])
async def get_anomaly_statistics(
    hours: int = Query(24, ge=1, le=168, description="统计时间范围(小时)"),
    current_user = Depends(get_current_user)
):
    """
    获取异常统计数据
    """
    anomalies = await anomaly_detection_service.get_recent_anomalies(hours=hours)
    
    # 统计各类型和严重程度的数量
    type_counts = {}
    severity_counts = {}
    province_counts = {}
    
    for a in anomalies:
        type_counts[a.type.value] = type_counts.get(a.type.value, 0) + 1
        severity_counts[a.severity.value] = severity_counts.get(a.severity.value, 0) + 1
        province_counts[a.province] = province_counts.get(a.province, 0) + 1
    
    return APIResponse.success_response({
        "total_count": len(anomalies),
        "time_range_hours": hours,
        "by_type": type_counts,
        "by_severity": severity_counts,
        "by_province": province_counts,
        "latest_anomaly": anomalies[0].to_dict() if anomalies else None
    })
