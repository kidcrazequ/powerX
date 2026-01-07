"""
PowerX 中国电力市场交易规则

创建日期: 2026-01-07
作者: zhi.qu

各省电力交易规则配置
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TradingRule:
    """交易规则"""
    province: str
    min_quantity_mwh: float  # 最小申报电量
    max_quantity_mwh: float  # 最大申报电量
    quantity_step_mwh: float  # 电量申报步长
    price_step: float  # 价格申报步长
    day_ahead_deadline: str  # 日前市场截止时间
    intraday_deadline: str  # 日内市场截止时间
    trading_hours: str  # 交易时段


# 各省交易规则
TRADING_RULES: Dict[str, TradingRule] = {
    "广东": TradingRule(
        province="广东",
        min_quantity_mwh=0.1,
        max_quantity_mwh=10000,
        quantity_step_mwh=0.1,
        price_step=0.01,
        day_ahead_deadline="10:00",
        intraday_deadline="T-1小时",
        trading_hours="24小时分时段"
    ),
    "浙江": TradingRule(
        province="浙江",
        min_quantity_mwh=0.1,
        max_quantity_mwh=10000,
        quantity_step_mwh=0.1,
        price_step=0.01,
        day_ahead_deadline="11:00",
        intraday_deadline="T-1小时",
        trading_hours="96时段（15分钟）"
    ),
    "山东": TradingRule(
        province="山东",
        min_quantity_mwh=0.1,
        max_quantity_mwh=10000,
        quantity_step_mwh=0.1,
        price_step=0.01,
        day_ahead_deadline="10:00",
        intraday_deadline="T-1小时",
        trading_hours="24小时分时段"
    ),
    "山西": TradingRule(
        province="山西",
        min_quantity_mwh=0.5,
        max_quantity_mwh=8000,
        quantity_step_mwh=0.5,
        price_step=0.1,
        day_ahead_deadline="10:00",
        intraday_deadline="T-1小时",
        trading_hours="24小时分时段"
    ),
    "甘肃": TradingRule(
        province="甘肃",
        min_quantity_mwh=0.5,
        max_quantity_mwh=5000,
        quantity_step_mwh=0.5,
        price_step=0.1,
        day_ahead_deadline="10:00",
        intraday_deadline="T-1小时",
        trading_hours="24小时分时段"
    )
}


def get_trading_rule(province: str) -> Optional[TradingRule]:
    """
    获取省份交易规则
    
    Args:
        province: 省份名称
        
    Returns:
        交易规则
    """
    return TRADING_RULES.get(province)


def validate_order(
    province: str,
    market_type: str,
    price: float,
    quantity_mwh: float,
    base_price: float
) -> Dict:
    """
    验证订单是否符合交易规则
    
    Args:
        province: 省份名称
        market_type: 市场类型
        price: 报价
        quantity_mwh: 电量
        base_price: 基准价格
        
    Returns:
        验证结果 {"valid": bool, "errors": List[str], "warnings": List[str]}
    """
    errors = []
    warnings = []
    
    rule = TRADING_RULES.get(province)
    if not rule:
        return {"valid": True, "errors": [], "warnings": ["未找到该省份交易规则，使用默认规则"]}
    
    # 验证电量
    if quantity_mwh < rule.min_quantity_mwh:
        errors.append(f"申报电量 {quantity_mwh} MWh 低于最小申报电量 {rule.min_quantity_mwh} MWh")
    
    if quantity_mwh > rule.max_quantity_mwh:
        errors.append(f"申报电量 {quantity_mwh} MWh 超过最大申报电量 {rule.max_quantity_mwh} MWh")
    
    # 验证电量步长
    remainder = quantity_mwh % rule.quantity_step_mwh
    if remainder > 0.001:  # 浮点数比较
        warnings.append(f"申报电量不是步长 {rule.quantity_step_mwh} MWh 的整数倍")
    
    # 验证价格步长
    price_remainder = (price * 100) % (rule.price_step * 100)
    if price_remainder > 0.001:
        warnings.append(f"申报价格不是步长 {rule.price_step} 元的整数倍")
    
    # 验证价格偏离
    if base_price > 0:
        deviation = abs(price - base_price) / base_price * 100
        if deviation > 50:
            warnings.append(f"价格偏离基准价 {deviation:.1f}%，超过 50% 警戒线")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def get_all_trading_rules() -> Dict[str, TradingRule]:
    """
    获取所有省份交易规则
    
    Returns:
        交易规则字典
    """
    return TRADING_RULES.copy()
