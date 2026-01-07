"""
PowerX 中国电力市场模块

创建日期: 2026-01-07
作者: zhi.qu

导出中国电力市场相关配置和规则
"""

from app.china_market.provinces import (
    get_province_config,
    get_all_provinces,
    is_province_supported,
    ProvinceConfig
)
from app.china_market.price_cap import (
    get_price_limits,
    validate_price,
    allows_negative_price,
    get_base_price
)
from app.china_market.trading_rules import (
    get_trading_rule,
    validate_order
)

__all__ = [
    # 省份配置
    "get_province_config",
    "get_all_provinces",
    "is_province_supported",
    "ProvinceConfig",
    # 限价规则
    "get_price_limits",
    "validate_price",
    "allows_negative_price",
    "get_base_price",
    # 交易规则
    "get_trading_rule",
    "validate_order"
]
