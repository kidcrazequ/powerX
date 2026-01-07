"""
PowerX 智能止损服务
创建日期: 2026-01-07
作者: zhi.qu

AI驱动的动态止损策略
"""
import math
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.conditional_order import ConditionalOrder


class StopLossStrategy(str, Enum):
    """止损策略类型"""
    FIXED = "fixed"               # 固定止损
    TRAILING = "trailing"         # 追踪止损
    ATR = "atr"                   # ATR波动率止损
    VOLATILITY = "volatility"     # 波动率自适应
    AI = "ai"                     # AI智能止损


@dataclass
class StopLossConfig:
    """止损配置"""
    strategy: StopLossStrategy
    trigger_price: float
    stop_price: float
    trailing_distance: Optional[float] = None  # 追踪距离
    atr_multiplier: Optional[float] = None     # ATR倍数
    volatility_threshold: Optional[float] = None  # 波动率阈值


@dataclass
class StopLossResult:
    """止损计算结果"""
    should_stop: bool
    current_stop_price: float
    trigger_price: float
    reason: str
    confidence: float


class StopLossService:
    """智能止损服务"""
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
        self._price_history: Dict[str, List[float]] = {}
    
    def calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """计算真实波动幅度均值 (ATR)"""
        if len(prices) < period + 1:
            return 0
        
        true_ranges = []
        for i in range(1, len(prices)):
            high = prices[i] * 1.01  # 模拟高价
            low = prices[i] * 0.99   # 模拟低价
            prev_close = prices[i - 1]
            
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)
        
        return sum(true_ranges[-period:]) / period
    
    def calculate_volatility(self, prices: List[float], period: int = 20) -> float:
        """计算波动率 (标准差)"""
        if len(prices) < period:
            return 0
        
        recent = prices[-period:]
        mean = sum(recent) / len(recent)
        variance = sum((p - mean) ** 2 for p in recent) / len(recent)
        return math.sqrt(variance)
    
    def calculate_trend(self, prices: List[float], period: int = 10) -> float:
        """计算趋势方向 (-1 到 1)"""
        if len(prices) < period:
            return 0
        
        recent = prices[-period:]
        x_mean = (period - 1) / 2
        y_mean = sum(recent) / len(recent)
        
        numerator = sum((i - x_mean) * (p - y_mean) for i, p in enumerate(recent))
        denominator = sum((i - x_mean) ** 2 for i in range(len(recent)))
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        # 归一化到 -1 到 1
        return max(-1, min(1, slope / (y_mean * 0.01)))
    
    def calculate_fixed_stop(
        self,
        entry_price: float,
        stop_percentage: float,
        order_type: str
    ) -> StopLossConfig:
        """计算固定止损"""
        if order_type == "buy":
            # 买入订单，价格下跌触发止损
            trigger_price = entry_price * (1 - stop_percentage / 100)
            stop_price = trigger_price * 0.99
        else:
            # 卖出订单，价格上涨触发止损
            trigger_price = entry_price * (1 + stop_percentage / 100)
            stop_price = trigger_price * 1.01
        
        return StopLossConfig(
            strategy=StopLossStrategy.FIXED,
            trigger_price=round(trigger_price, 2),
            stop_price=round(stop_price, 2)
        )
    
    def calculate_trailing_stop(
        self,
        current_price: float,
        highest_price: float,
        lowest_price: float,
        trailing_percentage: float,
        order_type: str
    ) -> StopLossConfig:
        """计算追踪止损"""
        if order_type == "buy":
            # 从最高价回撤
            trigger_price = highest_price * (1 - trailing_percentage / 100)
            stop_price = trigger_price * 0.99
            trailing_distance = highest_price - trigger_price
        else:
            # 从最低价反弹
            trigger_price = lowest_price * (1 + trailing_percentage / 100)
            stop_price = trigger_price * 1.01
            trailing_distance = trigger_price - lowest_price
        
        return StopLossConfig(
            strategy=StopLossStrategy.TRAILING,
            trigger_price=round(trigger_price, 2),
            stop_price=round(stop_price, 2),
            trailing_distance=round(trailing_distance, 2)
        )
    
    def calculate_atr_stop(
        self,
        entry_price: float,
        prices: List[float],
        atr_multiplier: float,
        order_type: str
    ) -> StopLossConfig:
        """计算 ATR 止损"""
        atr = self.calculate_atr(prices)
        
        if order_type == "buy":
            trigger_price = entry_price - atr * atr_multiplier
            stop_price = trigger_price * 0.99
        else:
            trigger_price = entry_price + atr * atr_multiplier
            stop_price = trigger_price * 1.01
        
        return StopLossConfig(
            strategy=StopLossStrategy.ATR,
            trigger_price=round(trigger_price, 2),
            stop_price=round(stop_price, 2),
            atr_multiplier=atr_multiplier
        )
    
    def calculate_ai_stop(
        self,
        entry_price: float,
        current_price: float,
        prices: List[float],
        order_type: str
    ) -> StopLossConfig:
        """AI智能止损计算
        
        综合考虑:
        1. 波动率
        2. 趋势方向
        3. 支撑/阻力位
        """
        volatility = self.calculate_volatility(prices)
        trend = self.calculate_trend(prices)
        atr = self.calculate_atr(prices)
        
        # 基础止损距离 (ATR的2倍)
        base_distance = atr * 2
        
        # 根据波动率调整
        if volatility > 10:  # 高波动
            volatility_factor = 1.5
        elif volatility > 5:  # 中波动
            volatility_factor = 1.2
        else:  # 低波动
            volatility_factor = 1.0
        
        # 根据趋势调整
        if order_type == "buy":
            if trend > 0.5:  # 强上涨趋势
                trend_factor = 0.8  # 收紧止损
            elif trend < -0.5:  # 强下跌趋势
                trend_factor = 1.3  # 放宽止损
            else:
                trend_factor = 1.0
        else:
            if trend < -0.5:  # 强下跌趋势
                trend_factor = 0.8
            elif trend > 0.5:  # 强上涨趋势
                trend_factor = 1.3
            else:
                trend_factor = 1.0
        
        # 最终止损距离
        stop_distance = base_distance * volatility_factor * trend_factor
        
        if order_type == "buy":
            trigger_price = current_price - stop_distance
            stop_price = trigger_price * 0.99
        else:
            trigger_price = current_price + stop_distance
            stop_price = trigger_price * 1.01
        
        return StopLossConfig(
            strategy=StopLossStrategy.AI,
            trigger_price=round(trigger_price, 2),
            stop_price=round(stop_price, 2),
            volatility_threshold=round(volatility, 2)
        )
    
    def evaluate_stop_loss(
        self,
        config: StopLossConfig,
        current_price: float,
        order_type: str
    ) -> StopLossResult:
        """评估是否触发止损"""
        if order_type == "buy":
            should_stop = current_price <= config.trigger_price
            reason = f"价格跌破止损线 {config.trigger_price}" if should_stop else "未触发"
        else:
            should_stop = current_price >= config.trigger_price
            reason = f"价格突破止损线 {config.trigger_price}" if should_stop else "未触发"
        
        # 计算置信度 (基于距离止损线的距离)
        distance = abs(current_price - config.trigger_price)
        distance_pct = distance / current_price * 100
        
        if should_stop:
            confidence = 1.0
        elif distance_pct < 1:
            confidence = 0.8  # 非常接近止损线
        elif distance_pct < 2:
            confidence = 0.5  # 接近止损线
        else:
            confidence = 0.2  # 远离止损线
        
        return StopLossResult(
            should_stop=should_stop,
            current_stop_price=config.stop_price,
            trigger_price=config.trigger_price,
            reason=reason,
            confidence=confidence
        )
    
    async def create_smart_stop_loss(
        self,
        user_id: str,
        order_id: str,
        order_type: str,
        entry_price: float,
        quantity: float,
        strategy: str = "ai",
        province: str = "guangdong"
    ) -> Dict[str, Any]:
        """创建智能止损订单"""
        # 获取历史价格
        prices = self._price_history.get(province, [entry_price] * 50)
        
        # 计算止损配置
        if strategy == "ai":
            config = self.calculate_ai_stop(entry_price, entry_price, prices, order_type)
        elif strategy == "atr":
            config = self.calculate_atr_stop(entry_price, prices, 2.0, order_type)
        elif strategy == "trailing":
            config = self.calculate_trailing_stop(
                entry_price, entry_price, entry_price, 3.0, order_type
            )
        else:
            config = self.calculate_fixed_stop(entry_price, 5.0, order_type)
        
        logger.info(f"创建智能止损: 订单 {order_id}, 策略 {strategy}, 触发价 {config.trigger_price}")
        
        return {
            "order_id": order_id,
            "strategy": config.strategy.value,
            "trigger_price": config.trigger_price,
            "stop_price": config.stop_price,
            "entry_price": entry_price,
            "quantity": quantity
        }
    
    def update_price_history(self, province: str, price: float):
        """更新价格历史"""
        if province not in self._price_history:
            self._price_history[province] = []
        
        self._price_history[province].append(price)
        
        # 只保留最近500个价格
        if len(self._price_history[province]) > 500:
            self._price_history[province] = self._price_history[province][-500:]


# 单例
stop_loss_service = StopLossService()


def get_stop_loss_service(db: AsyncSession = None) -> StopLossService:
    """获取止损服务"""
    if db:
        stop_loss_service.db = db
    return stop_loss_service
