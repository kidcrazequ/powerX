"""
PowerX 中国电力市场省份配置

创建日期: 2026-01-07
作者: zhi.qu

各省电力市场配置和特征
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ProvinceConfig:
    """省份配置"""
    name: str
    spot_market_active: bool
    price_mechanism: str  # node: 节点电价, zone: 分区电价, uniform: 统一出清
    settlement_period: int  # 结算周期（分钟）
    trading_center: str
    grid_company: str
    renewable_ratio: float  # 新能源占比
    peak_load_mw: int  # 最大负荷（MW）


# 省份配置
PROVINCE_CONFIGS: Dict[str, ProvinceConfig] = {
    "广东": ProvinceConfig(
        name="广东",
        spot_market_active=True,
        price_mechanism="node",
        settlement_period=15,
        trading_center="广东电力交易中心",
        grid_company="南方电网",
        renewable_ratio=0.15,
        peak_load_mw=150000
    ),
    "浙江": ProvinceConfig(
        name="浙江",
        spot_market_active=True,
        price_mechanism="uniform",
        settlement_period=15,
        trading_center="浙江电力交易中心",
        grid_company="国家电网",
        renewable_ratio=0.20,
        peak_load_mw=100000
    ),
    "山东": ProvinceConfig(
        name="山东",
        spot_market_active=True,
        price_mechanism="uniform",
        settlement_period=15,
        trading_center="山东电力交易中心",
        grid_company="国家电网",
        renewable_ratio=0.35,
        peak_load_mw=110000
    ),
    "山西": ProvinceConfig(
        name="山西",
        spot_market_active=True,
        price_mechanism="uniform",
        settlement_period=15,
        trading_center="山西电力交易中心",
        grid_company="国家电网",
        renewable_ratio=0.25,
        peak_load_mw=45000
    ),
    "甘肃": ProvinceConfig(
        name="甘肃",
        spot_market_active=True,
        price_mechanism="uniform",
        settlement_period=15,
        trading_center="甘肃电力交易中心",
        grid_company="国家电网",
        renewable_ratio=0.50,
        peak_load_mw=25000
    )
}


def get_province_config(province: str) -> Optional[ProvinceConfig]:
    """
    获取省份配置
    
    Args:
        province: 省份名称
        
    Returns:
        省份配置，不存在则返回 None
    """
    return PROVINCE_CONFIGS.get(province)


def get_all_provinces() -> List[str]:
    """
    获取所有支持的省份
    
    Returns:
        省份名称列表
    """
    return list(PROVINCE_CONFIGS.keys())


def is_province_supported(province: str) -> bool:
    """
    检查省份是否支持
    
    Args:
        province: 省份名称
        
    Returns:
        是否支持
    """
    return province in PROVINCE_CONFIGS


def get_price_caps(province: str) -> Dict[str, float]:
    """
    获取省份限价信息
    
    Args:
        province: 省份名称
        
    Returns:
        限价信息
    """
    from app.china_market.price_cap import get_price_limits
    min_price, max_price = get_price_limits(province)
    return {"min_price": min_price, "max_price": max_price}
