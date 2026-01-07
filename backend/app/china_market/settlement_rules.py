"""
PowerX 结算规则模块

创建日期: 2026-01-07
作者: zhi.qu

定义中国电力市场结算规则
"""

from typing import Dict, Optional
from dataclasses import dataclass
from loguru import logger

from app.china_market.provinces import get_province_config


@dataclass
class SettlementRule:
    """结算规则"""
    province: str
    deviation_threshold: float      # 偏差免考核阈值
    positive_deviation_rate: float  # 正偏差考核倍率（多发/少用）
    negative_deviation_rate: float  # 负偏差考核倍率（少发/多用）
    settlement_cycle: str           # 结算周期（daily/weekly/monthly）
    payment_cycle_days: int         # 付款周期（天）
    description: str


# 各省份结算规则
SETTLEMENT_RULES: Dict[str, SettlementRule] = {
    "广东": SettlementRule(
        province="广东",
        deviation_threshold=0.03,
        positive_deviation_rate=0.8,
        negative_deviation_rate=1.2,
        settlement_cycle="daily",
        payment_cycle_days=30,
        description="广东电力现货市场结算规则，日结算月清算"
    ),
    "浙江": SettlementRule(
        province="浙江",
        deviation_threshold=0.03,
        positive_deviation_rate=0.8,
        negative_deviation_rate=1.2,
        settlement_cycle="daily",
        payment_cycle_days=30,
        description="浙江电力现货市场结算规则，15分钟粒度结算"
    ),
    "山东": SettlementRule(
        province="山东",
        deviation_threshold=0.03,
        positive_deviation_rate=0.8,
        negative_deviation_rate=1.2,
        settlement_cycle="daily",
        payment_cycle_days=30,
        description="山东电力现货市场结算规则，含容量补偿结算"
    ),
    "山西": SettlementRule(
        province="山西",
        deviation_threshold=0.03,
        positive_deviation_rate=0.8,
        negative_deviation_rate=1.2,
        settlement_cycle="daily",
        payment_cycle_days=30,
        description="山西电力现货市场结算规则"
    ),
    "甘肃": SettlementRule(
        province="甘肃",
        deviation_threshold=0.05,
        positive_deviation_rate=0.7,
        negative_deviation_rate=1.3,
        settlement_cycle="daily",
        payment_cycle_days=30,
        description="甘肃电力现货市场结算规则，新能源偏差容忍度较高"
    ),
}


def get_settlement_rule(province: str) -> Optional[SettlementRule]:
    """
    获取省份结算规则
    
    Args:
        province: 省份名称
        
    Returns:
        Optional[SettlementRule]: 结算规则
    """
    return SETTLEMENT_RULES.get(province)


def calculate_deviation_settlement(
    province: str,
    contract_quantity_mwh: float,
    actual_quantity_mwh: float,
    settlement_price: float
) -> Dict[str, any]:
    """
    计算偏差结算
    
    Args:
        province: 省份名称
        contract_quantity_mwh: 合同电量（MWh）
        actual_quantity_mwh: 实际电量（MWh）
        settlement_price: 结算价格（元/MWh）
        
    Returns:
        Dict: 偏差结算结果
    """
    rule = get_settlement_rule(province)
    if rule is None:
        logger.warning(f"未找到结算规则: {province}，使用默认规则")
        rule = SettlementRule(
            province=province,
            deviation_threshold=0.03,
            positive_deviation_rate=0.8,
            negative_deviation_rate=1.2,
            settlement_cycle="daily",
            payment_cycle_days=30,
            description="默认结算规则"
        )
    
    # 计算偏差
    deviation_quantity = actual_quantity_mwh - contract_quantity_mwh
    
    if contract_quantity_mwh == 0:
        deviation_rate = 0.0
    else:
        deviation_rate = deviation_quantity / contract_quantity_mwh
    
    # 判断是否免考核
    is_exempt = abs(deviation_rate) <= rule.deviation_threshold
    
    # 计算偏差费用
    if is_exempt:
        deviation_amount = 0.0
        penalty_rate = 1.0
    elif deviation_rate > 0:
        # 正偏差（多发/少用）：按较低价格结算
        penalty_rate = rule.positive_deviation_rate
        deviation_amount = abs(deviation_quantity) * settlement_price * (1 - penalty_rate)
    else:
        # 负偏差（少发/多用）：按较高价格结算
        penalty_rate = rule.negative_deviation_rate
        deviation_amount = abs(deviation_quantity) * settlement_price * (penalty_rate - 1)
    
    return {
        "province": province,
        "contract_quantity_mwh": contract_quantity_mwh,
        "actual_quantity_mwh": actual_quantity_mwh,
        "deviation_quantity_mwh": deviation_quantity,
        "deviation_rate": deviation_rate,
        "deviation_rate_percent": deviation_rate * 100,
        "is_exempt": is_exempt,
        "threshold": rule.deviation_threshold,
        "penalty_rate": penalty_rate,
        "settlement_price": settlement_price,
        "deviation_amount": deviation_amount,
        "description": "正偏差（多发/少用）" if deviation_rate > 0 else "负偏差（少发/多用）" if deviation_rate < 0 else "无偏差"
    }


def calculate_spot_settlement(
    province: str,
    buy_quantity_mwh: float,
    sell_quantity_mwh: float,
    hourly_prices: list,
    hourly_quantities: list
) -> Dict[str, any]:
    """
    计算现货结算
    
    Args:
        province: 省份名称
        buy_quantity_mwh: 买入总电量
        sell_quantity_mwh: 卖出总电量
        hourly_prices: 各时段价格列表
        hourly_quantities: 各时段电量列表
        
    Returns:
        Dict: 现货结算结果
    """
    if len(hourly_prices) != len(hourly_quantities):
        logger.error("价格列表和电量列表长度不一致")
        return {"error": "数据不一致"}
    
    # 计算加权平均价格
    total_value = sum(p * q for p, q in zip(hourly_prices, hourly_quantities))
    total_quantity = sum(hourly_quantities)
    
    if total_quantity == 0:
        avg_price = 0.0
    else:
        avg_price = total_value / total_quantity
    
    # 计算买卖金额
    buy_amount = buy_quantity_mwh * avg_price
    sell_amount = sell_quantity_mwh * avg_price
    net_amount = sell_amount - buy_amount
    
    return {
        "province": province,
        "buy_quantity_mwh": buy_quantity_mwh,
        "sell_quantity_mwh": sell_quantity_mwh,
        "net_quantity_mwh": sell_quantity_mwh - buy_quantity_mwh,
        "avg_price": avg_price,
        "buy_amount": buy_amount,
        "sell_amount": sell_amount,
        "net_amount": net_amount,
        "hourly_count": len(hourly_prices)
    }
