"""
PowerX AI 服务 API

创建日期: 2026-01-07
作者: zhi.qu

AI 相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from app.ai.price_predictor import PricePredictor
from app.ai.strategy_engine import StrategyEngine
from app.ai.qa_assistant import QAAssistant
from app.ai.report_generator import ReportGenerator
from app.ai.load_predictor import load_predictor
from app.api.deps import get_current_user

router = APIRouter()


# ============ 请求/响应模型 ============

class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    context: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    """对话响应"""
    reply: str
    suggestions: Optional[List[str]] = None


class PredictionRequest(BaseModel):
    """价格预测请求"""
    province: str
    market_type: str = "DAY_AHEAD"  # DAY_AHEAD, INTRADAY
    hours: int = 24


class PredictionResponse(BaseModel):
    """价格预测响应"""
    province: str
    predictions: List[dict]
    summary: str
    confidence: float


class StrategyRequest(BaseModel):
    """策略请求"""
    province: str
    participant_type: str  # GENERATOR, RETAILER, LARGE_USER
    quantity_mwh: float
    risk_preference: str = "MEDIUM"  # LOW, MEDIUM, HIGH


class StrategyResponse(BaseModel):
    """策略响应"""
    strategies: List[dict]
    summary: str


class ReportRequest(BaseModel):
    """报告生成请求"""
    report_type: str  # DAILY, WEEKLY, MONTHLY
    start_date: date
    end_date: Optional[date] = None
    include_sections: Optional[List[str]] = None


class ReportResponse(BaseModel):
    """报告响应"""
    report_id: str
    title: str
    content: str
    generated_at: str


# ============ API 端点 ============

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user = Depends(get_current_user)
):
    """
    智能问答
    
    与 AI 助手对话，获取电力市场相关问题的解答
    """
    assistant = QAAssistant()
    
    try:
        reply = await assistant.answer_question(
            question=request.message,
            context=request.context
        )
        
        # 生成相关建议
        suggestions = [
            "广东明日电价预测",
            "推荐现货交易策略",
            "解读最新电力政策"
        ]
        
        return ChatResponse(
            reply=reply,
            suggestions=suggestions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 服务错误: {str(e)}")


@router.post("/predict", response_model=PredictionResponse)
async def predict_price(
    request: PredictionRequest,
    current_user = Depends(get_current_user)
):
    """
    电价预测
    
    预测指定省份未来电价走势
    """
    predictor = PricePredictor()
    
    try:
        result = await predictor.predict(
            province=request.province,
            market_type=request.market_type,
            hours=request.hours
        )
        
        return PredictionResponse(
            province=request.province,
            predictions=result["predictions"],
            summary=result["summary"],
            confidence=result["confidence"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测服务错误: {str(e)}")


@router.post("/strategy", response_model=StrategyResponse)
async def get_strategy(
    request: StrategyRequest,
    current_user = Depends(get_current_user)
):
    """
    策略推荐
    
    根据市场情况和用户特征推荐交易策略
    """
    engine = StrategyEngine()
    
    try:
        result = await engine.generate_strategy(
            province=request.province,
            participant_type=request.participant_type,
            quantity_mwh=request.quantity_mwh,
            risk_preference=request.risk_preference
        )
        
        return StrategyResponse(
            strategies=result["strategies"],
            summary=result["summary"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"策略服务错误: {str(e)}")


@router.post("/report", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    current_user = Depends(get_current_user)
):
    """
    生成报告
    
    自动生成交易分析报告
    """
    generator = ReportGenerator()
    
    try:
        result = await generator.generate(
            report_type=request.report_type,
            start_date=request.start_date,
            end_date=request.end_date,
            sections=request.include_sections
        )
        
        return ReportResponse(
            report_id=result["report_id"],
            title=result["title"],
            content=result["content"],
            generated_at=result["generated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成错误: {str(e)}")


@router.get("/capabilities")
async def get_ai_capabilities(
    current_user = Depends(get_current_user)
):
    """
    获取 AI 能力列表
    """
    return {
        "capabilities": [
            {
                "id": "chat",
                "name": "智能问答",
                "description": "回答电力市场相关问题，解读政策规则"
            },
            {
                "id": "predict",
                "name": "电价预测",
                "description": "预测未来24小时各省电价走势"
            },
            {
                "id": "strategy",
                "name": "策略推荐",
                "description": "根据市场情况推荐交易策略"
            },
            {
                "id": "report",
                "name": "报告生成",
                "description": "自动生成日报、周报、月报"
            },
            {
                "id": "forecast",
                "name": "电量预测",
                "description": "预测日/周/月电量和负荷曲线"
            }
        ]
    }


# ============ 电量预测 API ============

class ForecastRequest(BaseModel):
    """电量预测请求"""
    province: str
    forecast_type: str = "daily"  # daily, weekly, monthly
    target_date: Optional[date] = None
    year: Optional[int] = None
    month: Optional[int] = None


@router.post("/forecast")
async def forecast_load(
    request: ForecastRequest,
    current_user = Depends(get_current_user)
):
    """
    电量/负荷预测
    
    预测指定时间段的电量和负荷曲线
    """
    from datetime import date as date_type
    
    try:
        target = request.target_date or date_type.today()
        
        if request.forecast_type == "daily":
            result = await load_predictor.predict_daily_load(
                province=request.province,
                target_date=target
            )
        elif request.forecast_type == "weekly":
            result = await load_predictor.predict_weekly_load(
                province=request.province,
                start_date=target
            )
        elif request.forecast_type == "monthly":
            year = request.year or target.year
            month = request.month or target.month
            result = await load_predictor.predict_monthly_load(
                province=request.province,
                year=year,
                month=month
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的预测类型: {request.forecast_type}"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测服务错误: {str(e)}")


@router.get("/forecast/peak-valley/{province}")
async def get_peak_valley_forecast(
    province: str,
    target_date: Optional[date] = None,
    current_user = Depends(get_current_user)
):
    """
    峰谷时段预测
    
    预测指定日期的峰谷时段分布
    """
    from datetime import date as date_type
    
    try:
        target = target_date or date_type.today()
        result = await load_predictor.predict_peak_valley(province, target)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测服务错误: {str(e)}")
