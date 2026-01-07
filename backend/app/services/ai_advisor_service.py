"""
PowerX AI 交易顾问服务

创建日期: 2026-01-07
作者: zhi.qu

提供智能交易建议和市场分析功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import random
import math


class TradingRecommendation:
    """交易建议"""
    
    def __init__(
        self,
        id: str,
        province: str,
        market_type: str,
        direction: str,  # BUY/SELL/HOLD
        confidence: float,  # 0-1
        current_price: float,
        target_price: float,
        reason: str,
        factors: List[Dict[str, Any]],
        risk_level: str,  # LOW/MEDIUM/HIGH
        validity_hours: int = 4
    ):
        self.id = id
        self.province = province
        self.market_type = market_type
        self.direction = direction
        self.confidence = confidence
        self.current_price = current_price
        self.target_price = target_price
        self.reason = reason
        self.factors = factors
        self.risk_level = risk_level
        self.created_at = datetime.now()
        self.valid_until = datetime.now() + timedelta(hours=validity_hours)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "province": self.province,
            "market_type": self.market_type,
            "direction": self.direction,
            "confidence": self.confidence,
            "current_price": self.current_price,
            "target_price": self.target_price,
            "potential_profit_pct": round((self.target_price - self.current_price) / self.current_price * 100, 2),
            "reason": self.reason,
            "factors": self.factors,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat(),
            "valid_until": self.valid_until.isoformat()
        }


class AIAdvisorService:
    """AI 交易顾问服务"""
    
    PROVINCES = ["广东", "浙江", "江苏", "山东", "四川"]
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        logger.info("AIAdvisorService 初始化完成")
    
    async def analyze_market(
        self,
        province: str,
        market_type: str = "DAY_AHEAD"
    ) -> Dict[str, Any]:
        """
        分析市场状况
        
        Args:
            province: 省份
            market_type: 市场类型
            
        Returns:
            市场分析结果
        """
        logger.info(f"分析市场: {province} - {market_type}")
        
        # 模拟市场分析
        base_price = 450 + random.uniform(-50, 50)
        price_trend = random.choice(["UP", "DOWN", "STABLE"])
        volatility = random.uniform(0.05, 0.15)
        
        # 生成价格预测
        price_predictions = []
        current = base_price
        for i in range(24):
            change = random.gauss(0, base_price * 0.02)
            if price_trend == "UP":
                change += base_price * 0.005
            elif price_trend == "DOWN":
                change -= base_price * 0.005
            current += change
            price_predictions.append({
                "hour": i,
                "predicted_price": round(current, 2),
                "confidence": round(0.7 + random.uniform(-0.1, 0.1), 2)
            })
        
        # 市场情绪
        sentiment_score = random.uniform(-1, 1)
        if sentiment_score > 0.3:
            sentiment = "BULLISH"
        elif sentiment_score < -0.3:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"
        
        return {
            "province": province,
            "market_type": market_type,
            "analysis_time": datetime.now().isoformat(),
            "current_price": round(base_price, 2),
            "price_trend": price_trend,
            "volatility": round(volatility, 4),
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 2),
            "price_predictions": price_predictions,
            "key_factors": [
                {"factor": "供需平衡", "impact": random.choice(["POSITIVE", "NEGATIVE", "NEUTRAL"]), "weight": 0.3},
                {"factor": "天气预报", "impact": random.choice(["POSITIVE", "NEGATIVE", "NEUTRAL"]), "weight": 0.2},
                {"factor": "新能源出力", "impact": random.choice(["POSITIVE", "NEGATIVE", "NEUTRAL"]), "weight": 0.25},
                {"factor": "负荷预测", "impact": random.choice(["POSITIVE", "NEGATIVE", "NEUTRAL"]), "weight": 0.25}
            ],
            "risk_assessment": {
                "overall_risk": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "price_risk": round(random.uniform(0.1, 0.5), 2),
                "liquidity_risk": round(random.uniform(0.1, 0.3), 2)
            }
        }
    
    async def generate_recommendations(
        self,
        provinces: Optional[List[str]] = None,
        market_type: str = "DAY_AHEAD",
        limit: int = 5
    ) -> List[TradingRecommendation]:
        """
        生成交易建议
        
        Args:
            provinces: 省份列表
            market_type: 市场类型
            limit: 建议数量限制
            
        Returns:
            交易建议列表
        """
        if provinces is None:
            provinces = self.PROVINCES
        
        recommendations = []
        
        for province in provinces:
            # 分析市场
            analysis = await self.analyze_market(province, market_type)
            
            # 根据分析生成建议
            direction = "HOLD"
            confidence = 0.5
            reason = ""
            factors = []
            
            sentiment = analysis["sentiment"]
            price_trend = analysis["price_trend"]
            current_price = analysis["current_price"]
            
            if sentiment == "BULLISH" and price_trend != "DOWN":
                direction = "BUY"
                confidence = 0.6 + random.uniform(0, 0.2)
                reason = f"市场情绪偏多，价格趋势向上，建议逢低买入"
                factors = [
                    {"name": "市场情绪", "value": sentiment, "contribution": 0.4},
                    {"name": "价格趋势", "value": price_trend, "contribution": 0.3},
                    {"name": "供需分析", "value": "供应偏紧", "contribution": 0.3}
                ]
            elif sentiment == "BEARISH" and price_trend != "UP":
                direction = "SELL"
                confidence = 0.6 + random.uniform(0, 0.2)
                reason = f"市场情绪偏空，价格趋势向下，建议逢高卖出"
                factors = [
                    {"name": "市场情绪", "value": sentiment, "contribution": 0.4},
                    {"name": "价格趋势", "value": price_trend, "contribution": 0.3},
                    {"name": "供需分析", "value": "供应充裕", "contribution": 0.3}
                ]
            else:
                direction = "HOLD"
                confidence = 0.5 + random.uniform(0, 0.1)
                reason = f"市场观望情绪浓厚，建议暂时持仓观望"
                factors = [
                    {"name": "市场情绪", "value": sentiment, "contribution": 0.5},
                    {"name": "不确定性", "value": "较高", "contribution": 0.5}
                ]
            
            # 计算目标价格
            if direction == "BUY":
                target_price = current_price * (1 + random.uniform(0.02, 0.08))
            elif direction == "SELL":
                target_price = current_price * (1 - random.uniform(0.02, 0.08))
            else:
                target_price = current_price
            
            risk_level = analysis["risk_assessment"]["overall_risk"]
            
            rec = TradingRecommendation(
                id=f"REC-{province[:2]}-{datetime.now().strftime('%H%M%S')}-{random.randint(100, 999)}",
                province=province,
                market_type=market_type,
                direction=direction,
                confidence=round(confidence, 2),
                current_price=round(current_price, 2),
                target_price=round(target_price, 2),
                reason=reason,
                factors=factors,
                risk_level=risk_level
            )
            
            recommendations.append(rec)
        
        # 按置信度排序
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        
        return recommendations[:limit]
    
    async def get_opportunity_score(
        self,
        province: str,
        market_type: str = "DAY_AHEAD"
    ) -> Dict[str, Any]:
        """
        计算交易机会评分
        
        Args:
            province: 省份
            market_type: 市场类型
            
        Returns:
            机会评分
        """
        analysis = await self.analyze_market(province, market_type)
        
        # 计算综合评分 (0-100)
        base_score = 50
        
        # 情绪因素
        sentiment_score = analysis["sentiment_score"]
        base_score += sentiment_score * 15
        
        # 趋势因素
        if analysis["price_trend"] == "UP":
            base_score += 10
        elif analysis["price_trend"] == "DOWN":
            base_score -= 5
        
        # 波动率因素 (适中波动率加分)
        volatility = analysis["volatility"]
        if 0.08 < volatility < 0.12:
            base_score += 10
        elif volatility > 0.15:
            base_score -= 5
        
        # 风险调整
        risk = analysis["risk_assessment"]["overall_risk"]
        if risk == "LOW":
            base_score += 5
        elif risk == "HIGH":
            base_score -= 10
        
        # 限制在 0-100
        final_score = max(0, min(100, round(base_score)))
        
        return {
            "province": province,
            "market_type": market_type,
            "opportunity_score": final_score,
            "score_breakdown": {
                "sentiment_contribution": round(sentiment_score * 15, 1),
                "trend_contribution": 10 if analysis["price_trend"] == "UP" else (-5 if analysis["price_trend"] == "DOWN" else 0),
                "volatility_contribution": 10 if 0.08 < volatility < 0.12 else (-5 if volatility > 0.15 else 0),
                "risk_adjustment": 5 if risk == "LOW" else (-10 if risk == "HIGH" else 0)
            },
            "recommendation": "适合交易" if final_score >= 60 else ("观望为主" if final_score >= 40 else "不建议交易"),
            "analysis_summary": analysis
        }
    
    async def get_all_opportunities(self) -> List[Dict[str, Any]]:
        """获取所有省份的交易机会评分"""
        opportunities = []
        
        for province in self.PROVINCES:
            score = await self.get_opportunity_score(province)
            opportunities.append(score)
        
        # 按评分排序
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return opportunities


# 单例实例
ai_advisor_service = AIAdvisorService()


def get_ai_advisor_service(db: AsyncSession) -> AIAdvisorService:
    return AIAdvisorService(db)
