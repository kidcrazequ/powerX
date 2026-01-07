"""
PowerX 中国电力市场限价规则

创建日期: 2026-01-07
作者: zhi.qu

各省电力市场限价规则配置
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PriceCapRule:
    """限价规则"""
    province: str
    min_price: float
    max_price: float
    base_price: float
    allows_negative: bool
    max_deviation_percent: float  # 最大偏离百分比


# 各省限价规则
PRICE_CAP_RULES: Dict[str, PriceCapRule] = {
    "广东": PriceCapRule(
        province="广东",
        min_price=0,
        max_price=1500,
        base_price=463.0,
        allows_negative=False,
        max_deviation_percent=50
    ),
    "浙江": PriceCapRule(
        province="浙江",
        min_price=0,
        max_price=1500,
        base_price=475.0,
        allows_negative=False,
        max_deviation_percent=50
    ),
    "山东": PriceCapRule(
        province="山东",
        min_price=-100,
        max_price=1500,
        base_price=420.0,
        allows_negative=True,
        max_deviation_percent=50
    ),
    "山西": PriceCapRule(
        province="山西",
        min_price=0,
        max_price=1500,
        base_price=380.0,
        allows_negative=False,
        max_deviation_percent=50
    ),
    "甘肃": PriceCapRule(
        province="甘肃",
        min_price=-50,
        max_price=1500,
        base_price=350.0,
        allows_negative=True,
        max_deviation_percent=50
    )
}


def get_price_limits(province: str) -> Tuple[float, float]:
    """
    获取省份价格限制
    
    Args:
        province: 省份名称
        
    Returns:
        (最低价, 最高价) 元组
    """
    rule = PRICE_CAP_RULES.get(province)
    if not rule:
        # 默认限价
        return (0, 1500)
    return (rule.min_price, rule.max_price)


def validate_price(province: str, price: float) -> Dict:
    """
    验证价格是否在允许范围内
    
    Args:
        province: 省份名称
        price: 价格
        
    Returns:
        验证结果 {"valid": bool, "error": str}
    """
    rule = PRICE_CAP_RULES.get(province)
    if not rule:
        return {"valid": True, "error": None}
    
    # 检查负价
    if price < 0 and not rule.allows_negative:
        return {
            "valid": False,
            "error": f"{province}省不允许负电价"
        }
    
    # 检查最低价
    if price < rule.min_price:
        return {
            "valid": False,
            "error": f"价格 {price} 低于最低限价 {rule.min_price}"
        }
    
    # 检查最高价
    if price > rule.max_price:
        return {
            "valid": False,
            "error": f"价格 {price} 高于最高限价 {rule.max_price}"
        }
    
    return {"valid": True, "error": None}


def allows_negative_price(province: str) -> bool:
    """
    检查省份是否允许负电价
    
    Args:
        province: 省份名称
        
    Returns:
        是否允许负电价
    """
    rule = PRICE_CAP_RULES.get(province)
    return rule.allows_negative if rule else False


def get_base_price(province: str) -> float:
    """
    获取省份基准价格
    
    Args:
        province: 省份名称
        
    Returns:
        基准价格
    """
    rule = PRICE_CAP_RULES.get(province)
    return rule.base_price if rule else 450.0


def get_deviation_limit(province: str, base_price: float) -> Tuple[float, float]:
    """
    获取价格偏离限制
    
    Args:
        province: 省份名称
        base_price: 基准价格
        
    Returns:
        (最低偏离价, 最高偏离价) 元组
    """
    rule = PRICE_CAP_RULES.get(province)
    if not rule:
        return (base_price * 0.5, base_price * 1.5)
    
    deviation = base_price * (rule.max_deviation_percent / 100)
    min_dev = max(rule.min_price, base_price - deviation)
    max_dev = min(rule.max_price, base_price + deviation)
    
    return (min_dev, max_dev)
