"""
PowerX 异常检测服务

创建日期: 2026-01-07
作者: zhi.qu

提供价格、交易量和交易模式的异常检测功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import random
import math
from dataclasses import dataclass
from enum import Enum


class AnomalyType(str, Enum):
    """异常类型"""
    PRICE_SPIKE = "PRICE_SPIKE"           # 价格飙升
    PRICE_CRASH = "PRICE_CRASH"           # 价格暴跌
    VOLUME_SURGE = "VOLUME_SURGE"         # 成交量激增
    VOLUME_DROP = "VOLUME_DROP"           # 成交量骤降
    PATTERN_UNUSUAL = "PATTERN_UNUSUAL"   # 异常交易模式
    SPREAD_ABNORMAL = "SPREAD_ABNORMAL"   # 价差异常


class AnomalySeverity(str, Enum):
    """异常严重程度"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Anomaly:
    """异常实体"""
    id: str
    type: AnomalyType
    severity: AnomalySeverity
    province: str
    market_type: str
    detected_at: datetime
    description: str
    current_value: float
    expected_value: float
    deviation: float  # 偏离程度
    details: Dict[str, Any]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "province": self.province,
            "market_type": self.market_type,
            "detected_at": self.detected_at.isoformat(),
            "description": self.description,
            "current_value": self.current_value,
            "expected_value": self.expected_value,
            "deviation": round(self.deviation, 4),
            "deviation_pct": round(self.deviation * 100, 2),
            "details": self.details,
            "recommendations": self.recommendations
        }


class AnomalyDetectionService:
    """异常检测服务"""
    
    # 阈值配置
    THRESHOLDS = {
        "price_spike": 0.10,      # 价格上涨超过10%
        "price_crash": -0.10,     # 价格下跌超过10%
        "volume_surge": 2.0,      # 成交量是平均的2倍
        "volume_drop": 0.3,       # 成交量低于平均的30%
        "spread_abnormal": 50.0,  # 价差超过50元/MWh
    }
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        self.anomaly_history: List[Anomaly] = []
        logger.info("AnomalyDetectionService 初始化完成")
    
    async def detect_price_anomaly(
        self,
        province: str,
        current_price: float,
        historical_prices: List[float],
        market_type: str = "DAY_AHEAD"
    ) -> Optional[Anomaly]:
        """
        检测价格异常
        
        Args:
            province: 省份
            current_price: 当前价格
            historical_prices: 历史价格列表
            market_type: 市场类型
            
        Returns:
            检测到的异常，如果没有则返回 None
        """
        if len(historical_prices) < 3:
            return None
        
        # 计算平均价格和标准差
        avg_price = sum(historical_prices) / len(historical_prices)
        variance = sum((p - avg_price) ** 2 for p in historical_prices) / len(historical_prices)
        std_price = math.sqrt(variance) if variance > 0 else 1
        
        # 计算偏离程度
        deviation = (current_price - avg_price) / avg_price
        z_score = (current_price - avg_price) / std_price if std_price > 0 else 0
        
        anomaly = None
        
        if deviation > self.THRESHOLDS["price_spike"]:
            # 价格飙升
            severity = self._get_severity(abs(deviation), 0.10, 0.20, 0.30)
            anomaly = Anomaly(
                id=f"ANO-PRICE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
                type=AnomalyType.PRICE_SPIKE,
                severity=severity,
                province=province,
                market_type=market_type,
                detected_at=datetime.now(),
                description=f"{province}电价异常飙升，当前价格 {current_price:.2f} 元/MWh，偏离均值 {deviation*100:.1f}%",
                current_value=current_price,
                expected_value=avg_price,
                deviation=deviation,
                details={
                    "z_score": round(z_score, 2),
                    "historical_avg": round(avg_price, 2),
                    "historical_std": round(std_price, 2),
                    "sample_size": len(historical_prices)
                },
                recommendations=[
                    "密切关注市场动态，可能存在供应紧张",
                    "考虑逢高卖出已有持仓",
                    "设置止损点位防范风险"
                ]
            )
            
        elif deviation < self.THRESHOLDS["price_crash"]:
            # 价格暴跌
            severity = self._get_severity(abs(deviation), 0.10, 0.20, 0.30)
            anomaly = Anomaly(
                id=f"ANO-PRICE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
                type=AnomalyType.PRICE_CRASH,
                severity=severity,
                province=province,
                market_type=market_type,
                detected_at=datetime.now(),
                description=f"{province}电价异常暴跌，当前价格 {current_price:.2f} 元/MWh，偏离均值 {deviation*100:.1f}%",
                current_value=current_price,
                expected_value=avg_price,
                deviation=deviation,
                details={
                    "z_score": round(z_score, 2),
                    "historical_avg": round(avg_price, 2),
                    "historical_std": round(std_price, 2),
                    "sample_size": len(historical_prices)
                },
                recommendations=[
                    "可能是买入良机，但需确认是否为短期波动",
                    "检查是否有重大供需变化",
                    "分批建仓降低风险"
                ]
            )
        
        if anomaly:
            self.anomaly_history.append(anomaly)
            logger.warning(f"检测到价格异常: {anomaly.type.value}, 省份={province}, 偏离={deviation*100:.1f}%")
        
        return anomaly
    
    async def detect_volume_anomaly(
        self,
        province: str,
        current_volume: float,
        historical_volumes: List[float],
        market_type: str = "DAY_AHEAD"
    ) -> Optional[Anomaly]:
        """
        检测成交量异常
        
        Args:
            province: 省份
            current_volume: 当前成交量
            historical_volumes: 历史成交量列表
            market_type: 市场类型
            
        Returns:
            检测到的异常
        """
        if len(historical_volumes) < 3:
            return None
        
        avg_volume = sum(historical_volumes) / len(historical_volumes)
        ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        anomaly = None
        
        if ratio > self.THRESHOLDS["volume_surge"]:
            severity = self._get_severity(ratio, 2.0, 3.0, 5.0)
            anomaly = Anomaly(
                id=f"ANO-VOL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
                type=AnomalyType.VOLUME_SURGE,
                severity=severity,
                province=province,
                market_type=market_type,
                detected_at=datetime.now(),
                description=f"{province}成交量异常激增，当前成交量 {current_volume:.0f} MWh，是平均水平的 {ratio:.1f} 倍",
                current_value=current_volume,
                expected_value=avg_volume,
                deviation=ratio - 1,
                details={
                    "volume_ratio": round(ratio, 2),
                    "historical_avg": round(avg_volume, 0)
                },
                recommendations=[
                    "市场活跃度显著提升，注意把握交易机会",
                    "关注是否有重大政策或事件发生",
                    "可能预示价格即将大幅波动"
                ]
            )
            
        elif ratio < self.THRESHOLDS["volume_drop"]:
            severity = self._get_severity(1/ratio if ratio > 0 else 10, 3.0, 5.0, 10.0)
            anomaly = Anomaly(
                id=f"ANO-VOL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
                type=AnomalyType.VOLUME_DROP,
                severity=severity,
                province=province,
                market_type=market_type,
                detected_at=datetime.now(),
                description=f"{province}成交量异常萎缩，当前成交量 {current_volume:.0f} MWh，仅为平均水平的 {ratio*100:.0f}%",
                current_value=current_volume,
                expected_value=avg_volume,
                deviation=ratio - 1,
                details={
                    "volume_ratio": round(ratio, 2),
                    "historical_avg": round(avg_volume, 0)
                },
                recommendations=[
                    "市场流动性下降，交易时注意滑点风险",
                    "大额订单可能难以快速成交",
                    "考虑分批执行交易策略"
                ]
            )
        
        if anomaly:
            self.anomaly_history.append(anomaly)
            logger.warning(f"检测到成交量异常: {anomaly.type.value}, 省份={province}")
        
        return anomaly
    
    async def detect_pattern_anomaly(
        self,
        province: str,
        trade_pattern: Dict[str, Any],
        market_type: str = "DAY_AHEAD"
    ) -> Optional[Anomaly]:
        """
        检测交易模式异常
        
        Args:
            province: 省份
            trade_pattern: 交易模式数据
            market_type: 市场类型
            
        Returns:
            检测到的异常
        """
        # 模拟检测结果
        if random.random() < 0.1:  # 10% 概率检测到异常
            anomaly = Anomaly(
                id=f"ANO-PATTERN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
                type=AnomalyType.PATTERN_UNUSUAL,
                severity=AnomalySeverity.MEDIUM,
                province=province,
                market_type=market_type,
                detected_at=datetime.now(),
                description=f"{province}检测到异常交易模式，可能存在市场操纵行为",
                current_value=0,
                expected_value=0,
                deviation=0,
                details={
                    "pattern_type": "集中交易",
                    "confidence": round(random.uniform(0.6, 0.9), 2)
                },
                recommendations=[
                    "建议暂时观望，避免跟风操作",
                    "密切关注后续市场走势",
                    "如有持仓考虑设置止损"
                ]
            )
            self.anomaly_history.append(anomaly)
            logger.warning(f"检测到模式异常: {province}")
            return anomaly
        
        return None
    
    async def run_full_detection(
        self,
        province: str,
        market_data: Dict[str, Any]
    ) -> List[Anomaly]:
        """
        运行完整异常检测
        
        Args:
            province: 省份
            market_data: 市场数据，包含 current_price, current_volume, historical_prices, historical_volumes
            
        Returns:
            检测到的所有异常
        """
        anomalies = []
        
        # 价格异常检测
        if "current_price" in market_data and "historical_prices" in market_data:
            price_anomaly = await self.detect_price_anomaly(
                province=province,
                current_price=market_data["current_price"],
                historical_prices=market_data["historical_prices"],
                market_type=market_data.get("market_type", "DAY_AHEAD")
            )
            if price_anomaly:
                anomalies.append(price_anomaly)
        
        # 成交量异常检测
        if "current_volume" in market_data and "historical_volumes" in market_data:
            volume_anomaly = await self.detect_volume_anomaly(
                province=province,
                current_volume=market_data["current_volume"],
                historical_volumes=market_data["historical_volumes"],
                market_type=market_data.get("market_type", "DAY_AHEAD")
            )
            if volume_anomaly:
                anomalies.append(volume_anomaly)
        
        # 模式异常检测
        pattern_anomaly = await self.detect_pattern_anomaly(
            province=province,
            trade_pattern=market_data,
            market_type=market_data.get("market_type", "DAY_AHEAD")
        )
        if pattern_anomaly:
            anomalies.append(pattern_anomaly)
        
        return anomalies
    
    async def get_recent_anomalies(
        self,
        hours: int = 24,
        severity: Optional[str] = None,
        province: Optional[str] = None
    ) -> List[Anomaly]:
        """获取最近的异常"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        result = [
            a for a in self.anomaly_history
            if a.detected_at >= cutoff
        ]
        
        if severity:
            result = [a for a in result if a.severity.value == severity]
        
        if province:
            result = [a for a in result if a.province == province]
        
        return sorted(result, key=lambda a: a.detected_at, reverse=True)
    
    def _get_severity(
        self,
        value: float,
        low_threshold: float,
        medium_threshold: float,
        high_threshold: float
    ) -> AnomalySeverity:
        """根据值确定严重程度"""
        if value >= high_threshold:
            return AnomalySeverity.CRITICAL
        elif value >= medium_threshold:
            return AnomalySeverity.HIGH
        elif value >= low_threshold:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW


# 单例实例
anomaly_detection_service = AnomalyDetectionService()


def get_anomaly_detection_service(db: AsyncSession) -> AnomalyDetectionService:
    return AnomalyDetectionService(db)
