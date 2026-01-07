"""
PowerX 风险敞口服务

创建日期: 2026-01-07
作者: zhi.qu

提供风险敞口计算和监控功能
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import random


class ExposureService:
    """风险敞口服务"""
    
    def __init__(self):
        logger.info("ExposureService 初始化完成")
    
    async def calculate_exposure(self, user_id: str) -> Dict[str, Any]:
        """
        计算用户风险敞口
        
        Args:
            user_id: 用户ID
            
        Returns:
            敞口计算结果
        """
        # 模拟敞口计算
        long_position = random.uniform(500, 2000)  # 多头持仓
        short_position = random.uniform(300, 1500)  # 空头持仓
        net_exposure = long_position - short_position
        
        return {
            "user_id": user_id,
            "calculated_at": datetime.now().isoformat(),
            "long_position_mwh": round(long_position, 2),
            "short_position_mwh": round(short_position, 2),
            "net_exposure_mwh": round(net_exposure, 2),
            "gross_exposure_mwh": round(long_position + short_position, 2),
            "exposure_ratio": round(abs(net_exposure) / (long_position + short_position) * 100, 2),
            "risk_level": self._get_risk_level(abs(net_exposure))
        }
    
    def _get_risk_level(self, net_exposure: float) -> str:
        """根据净敞口判断风险等级"""
        if net_exposure < 500:
            return "low"
        elif net_exposure < 1000:
            return "medium"
        else:
            return "high"
    
    async def get_exposure_breakdown(self, user_id: str) -> Dict[str, Any]:
        """
        获取敞口分解
        
        Args:
            user_id: 用户ID
            
        Returns:
            敞口分解详情
        """
        provinces = ["广东", "浙江", "山东", "江苏", "四川"]
        breakdown = {}
        
        for province in provinces:
            long_pos = random.uniform(50, 400)
            short_pos = random.uniform(30, 300)
            breakdown[province] = {
                "long_mwh": round(long_pos, 2),
                "short_mwh": round(short_pos, 2),
                "net_mwh": round(long_pos - short_pos, 2)
            }
        
        return {
            "user_id": user_id,
            "by_province": breakdown,
            "by_market": {
                "spot": {"long_mwh": round(random.uniform(200, 800), 2),
                        "short_mwh": round(random.uniform(100, 600), 2)},
                "contract": {"long_mwh": round(random.uniform(300, 1000), 2),
                            "short_mwh": round(random.uniform(200, 800), 2)}
            }
        }
    
    async def get_var(self, user_id: str, confidence: float = 0.95) -> Dict[str, Any]:
        """
        计算VaR(风险价值)
        
        Args:
            user_id: 用户ID
            confidence: 置信水平
            
        Returns:
            VaR计算结果
        """
        # 模拟VaR计算
        var_value = random.uniform(10000, 50000)
        
        return {
            "user_id": user_id,
            "confidence_level": confidence,
            "var_1day": round(var_value, 2),
            "var_5day": round(var_value * 2.24, 2),  # sqrt(5) * var_1day
            "var_10day": round(var_value * 3.16, 2),  # sqrt(10) * var_1day
            "expected_shortfall": round(var_value * 1.25, 2),
            "currency": "CNY"
        }
    
    async def check_exposure_limits(self, user_id: str) -> Dict[str, Any]:
        """检查敞口是否超限"""
        exposure = await self.calculate_exposure(user_id)
        
        warnings = []
        if exposure["exposure_ratio"] > 70:
            warnings.append({"type": "high_exposure_ratio", "message": "敞口比例超过70%"})
        if exposure["gross_exposure_mwh"] > 3000:
            warnings.append({"type": "high_gross_exposure", "message": "总敞口超过3000MWh"})
        if exposure["risk_level"] == "high":
            warnings.append({"type": "high_risk_level", "message": "风险等级为高"})
        
        return {
            "exposure": exposure,
            "within_limits": len(warnings) == 0,
            "warnings": warnings
        }


# 单例实例
exposure_service = ExposureService()


def get_exposure_service() -> ExposureService:
    return exposure_service
