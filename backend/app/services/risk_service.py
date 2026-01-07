"""
PowerX 风险服务

创建日期: 2026-01-07
作者: zhi.qu

提供风险评估、预警等功能
"""

from typing import Dict, List, Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.constants import RiskLevel, MarketType
from app.china_market.price_cap import get_base_price, get_price_limits


class RiskService:
    """风险服务类"""
    
    def __init__(self, db: Optional[AsyncSession] = None):
        """
        初始化风险服务
        
        Args:
            db: 数据库会话（可选）
        """
        self.db = db
    
    def assess_position_risk(
        self,
        province: str,
        position_mwh: float,
        avg_cost: float,
        current_price: Optional[float] = None,
        market_type: MarketType = MarketType.DAY_AHEAD
    ) -> Dict:
        """
        评估持仓风险
        
        Args:
            province: 省份
            position_mwh: 持仓量（MWh）
            avg_cost: 平均成本（元/MWh）
            current_price: 当前价格（元/MWh）
            market_type: 市场类型
            
        Returns:
            Dict: 风险评估结果
        """
        logger.info(f"评估持仓风险: province={province}, position={position_mwh}")
        
        base_price = get_base_price(province)
        min_price, max_price = get_price_limits(province)
        
        if current_price is None:
            current_price = base_price
        
        # 计算未实现盈亏
        unrealized_pnl = (current_price - avg_cost) * position_mwh
        
        # 计算风险指标
        risk_factors = []
        risk_score = 0
        
        # 1. 持仓规模风险
        position_value = abs(position_mwh * current_price)
        if position_value > 1000000:
            risk_factors.append({
                "type": "position_size",
                "level": "HIGH",
                "description": f"持仓价值 {position_value:.0f} 元，规模较大"
            })
            risk_score += 30
        elif position_value > 500000:
            risk_factors.append({
                "type": "position_size",
                "level": "MEDIUM",
                "description": f"持仓价值 {position_value:.0f} 元，规模适中"
            })
            risk_score += 15
        
        # 2. 价格偏离风险
        price_deviation = (current_price - base_price) / base_price
        if abs(price_deviation) > 0.3:
            risk_factors.append({
                "type": "price_deviation",
                "level": "HIGH",
                "description": f"当前价格偏离基准 {price_deviation*100:.1f}%"
            })
            risk_score += 25
        elif abs(price_deviation) > 0.15:
            risk_factors.append({
                "type": "price_deviation",
                "level": "MEDIUM",
                "description": f"当前价格偏离基准 {price_deviation*100:.1f}%"
            })
            risk_score += 10
        
        # 3. 方向风险
        if position_mwh > 0 and current_price > base_price * 1.2:
            risk_factors.append({
                "type": "direction",
                "level": "MEDIUM",
                "description": "多头持仓，当前价格处于高位"
            })
            risk_score += 15
        elif position_mwh < 0 and current_price < base_price * 0.8:
            risk_factors.append({
                "type": "direction",
                "level": "MEDIUM",
                "description": "空头持仓，当前价格处于低位"
            })
            risk_score += 15
        
        # 计算 VaR (95%)
        # 简化计算：假设价格波动 10%
        volatility = 0.1
        var_95 = abs(position_mwh * current_price * volatility * 1.65)
        
        # 计算最大损失估计
        if position_mwh > 0:
            # 多头：价格跌到最低
            max_loss = (avg_cost - min_price) * position_mwh
        else:
            # 空头：价格涨到最高
            max_loss = (max_price - avg_cost) * abs(position_mwh)
        
        # 确定风险等级
        if risk_score >= 60:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 40:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 20:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # 生成建议
        recommendations = self._generate_recommendations(
            risk_level, risk_factors, position_mwh, unrealized_pnl
        )
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "max_loss_estimate": max(0, max_loss),
            "var_95": var_95,
            "unrealized_pnl": unrealized_pnl,
            "current_price": current_price,
            "base_price": base_price,
            "assessed_at": datetime.now().isoformat()
        }
    
    def check_price_alert(
        self,
        province: str,
        current_price: float,
        threshold_high: Optional[float] = None,
        threshold_low: Optional[float] = None
    ) -> List[Dict]:
        """
        检查价格预警
        
        Args:
            province: 省份
            current_price: 当前价格
            threshold_high: 高价阈值
            threshold_low: 低价阈值
            
        Returns:
            List[Dict]: 预警列表
        """
        base_price = get_base_price(province)
        min_price, max_price = get_price_limits(province)
        
        alerts = []
        
        # 默认阈值
        if threshold_high is None:
            threshold_high = base_price * 1.3
        if threshold_low is None:
            threshold_low = base_price * 0.7
        
        # 检查高价预警
        if current_price >= threshold_high:
            alerts.append({
                "type": "HIGH_PRICE",
                "level": "WARNING",
                "message": f"当前电价 {current_price:.2f} 元/MWh 超过预警阈值 {threshold_high:.2f}",
                "timestamp": datetime.now().isoformat()
            })
        
        # 检查低价预警
        if current_price <= threshold_low:
            alerts.append({
                "type": "LOW_PRICE",
                "level": "INFO",
                "message": f"当前电价 {current_price:.2f} 元/MWh 低于预警阈值 {threshold_low:.2f}",
                "timestamp": datetime.now().isoformat()
            })
        
        # 检查极端价格
        if current_price >= max_price * 0.9:
            alerts.append({
                "type": "EXTREME_HIGH",
                "level": "CRITICAL",
                "message": f"当前电价 {current_price:.2f} 元/MWh 接近限价上限",
                "timestamp": datetime.now().isoformat()
            })
        
        if current_price <= min_price * 1.1 or (min_price < 0 and current_price < 50):
            alerts.append({
                "type": "EXTREME_LOW",
                "level": "CRITICAL",
                "message": f"当前电价 {current_price:.2f} 元/MWh 接近限价下限",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        risk_factors: List[Dict],
        position_mwh: float,
        unrealized_pnl: float
    ) -> List[str]:
        """生成风险建议"""
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("建议立即评估并调整持仓")
            if abs(position_mwh) > 500:
                recommendations.append("考虑分批减少持仓以降低风险敞口")
        
        if unrealized_pnl < 0 and abs(unrealized_pnl) > 50000:
            recommendations.append(f"当前浮亏 {abs(unrealized_pnl):.0f} 元，注意止损")
        elif unrealized_pnl > 50000:
            recommendations.append(f"当前浮盈 {unrealized_pnl:.0f} 元，可考虑部分止盈")
        
        for factor in risk_factors:
            if factor["type"] == "price_deviation" and factor["level"] == "HIGH":
                recommendations.append("价格偏离较大，关注市场变化及时调整策略")
        
        if not recommendations:
            recommendations.append("当前风险可控，建议继续保持观察")
        
        return recommendations
    
    async def assess_risk(
        self,
        user_id: str,
        province: str,
        position_mwh: Optional[float] = None,
        avg_cost: Optional[float] = None
    ) -> Dict:
        """
        综合风险评估（便捷方法）
        
        整合持仓风险评估和价格预警，为 API 层提供统一接口
        
        Args:
            user_id: 用户 ID
            province: 省份名称
            position_mwh: 持仓量（MWh），None 时使用默认模拟值
            avg_cost: 平均成本（元/MWh），None 时使用基准价
            
        Returns:
            Dict: 综合风险评估结果
        """
        logger.info(f"综合风险评估: user_id={user_id}, province={province}")
        
        base_price = get_base_price(province)
        
        # 如果未提供参数，使用模拟数据
        if position_mwh is None:
            position_mwh = 1000.0  # 默认持仓
        if avg_cost is None:
            avg_cost = base_price * 0.98  # 假设成本略低于基准价
        
        # 获取当前市场价格（模拟）
        import random
        current_price = base_price * (1 + random.uniform(-0.1, 0.1))
        
        # 持仓风险评估
        position_risk = self.assess_position_risk(
            province=province,
            position_mwh=position_mwh,
            avg_cost=avg_cost,
            current_price=current_price
        )
        
        # 价格预警检查
        price_alerts = self.check_price_alert(
            province=province,
            current_price=current_price
        )
        
        # 计算综合风险得分
        overall_score = position_risk["risk_score"]
        if len(price_alerts) > 0:
            # 每个预警增加 10 分
            overall_score += len(price_alerts) * 10
        
        # 确定综合风险等级
        if overall_score >= 70:
            overall_level = RiskLevel.CRITICAL
        elif overall_score >= 50:
            overall_level = RiskLevel.HIGH
        elif overall_score >= 30:
            overall_level = RiskLevel.MEDIUM
        else:
            overall_level = RiskLevel.LOW
        
        return {
            "user_id": user_id,
            "province": province,
            "overall_risk_level": overall_level,
            "overall_risk_score": min(100, overall_score),
            "position_risk": position_risk,
            "price_alerts": price_alerts,
            "market_status": {
                "current_price": round(current_price, 2),
                "base_price": base_price,
                "price_change_percent": round((current_price - base_price) / base_price * 100, 2)
            },
            "assessed_at": datetime.now().isoformat()
        }
    
    async def get_risk_alerts(
        self,
        user_id: str,
        province: str,
        include_position_alerts: bool = True,
        include_price_alerts: bool = True
    ) -> List[Dict]:
        """
        获取风险预警列表（便捷方法）
        
        汇总所有类型的风险预警，为 API 层提供统一接口
        
        Args:
            user_id: 用户 ID
            province: 省份名称
            include_position_alerts: 是否包含持仓预警
            include_price_alerts: 是否包含价格预警
            
        Returns:
            List[Dict]: 风险预警列表
        """
        logger.info(f"获取风险预警: user_id={user_id}, province={province}")
        
        alerts = []
        base_price = get_base_price(province)
        
        # 模拟当前价格
        import random
        current_price = base_price * (1 + random.uniform(-0.15, 0.15))
        
        # 价格预警
        if include_price_alerts:
            price_alerts = self.check_price_alert(
                province=province,
                current_price=current_price
            )
            for alert in price_alerts:
                alert["category"] = "price"
                alert["province"] = province
                alerts.append(alert)
        
        # 持仓预警（基于模拟数据）
        if include_position_alerts:
            # 模拟持仓数据
            position_mwh = random.uniform(500, 2000)
            avg_cost = base_price * random.uniform(0.9, 1.1)
            
            position_risk = self.assess_position_risk(
                province=province,
                position_mwh=position_mwh,
                avg_cost=avg_cost,
                current_price=current_price
            )
            
            # 将高风险因素转换为预警
            for factor in position_risk["risk_factors"]:
                if factor["level"] in ["HIGH", "CRITICAL"]:
                    alerts.append({
                        "type": f"POSITION_{factor['type'].upper()}",
                        "level": factor["level"],
                        "category": "position",
                        "province": province,
                        "message": factor["description"],
                        "timestamp": datetime.now().isoformat()
                    })
            
            # 如果整体风险等级较高，添加综合预警
            if position_risk["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                alerts.append({
                    "type": "OVERALL_RISK",
                    "level": position_risk["risk_level"].value,
                    "category": "overall",
                    "province": province,
                    "message": f"整体风险等级为 {position_risk['risk_level'].value}，风险得分 {position_risk['risk_score']}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # 按严重程度排序（CRITICAL > HIGH > WARNING > INFO）
        level_order = {"CRITICAL": 0, "HIGH": 1, "WARNING": 2, "MEDIUM": 3, "INFO": 4, "LOW": 5}
        alerts.sort(key=lambda x: level_order.get(x.get("level", "INFO"), 99))
        
        logger.info(f"共生成 {len(alerts)} 条风险预警")
        return alerts


# 创建全局风险服务实例
risk_service = RiskService()
