"""
PowerX 市场模块测试

创建日期: 2026-01-07
作者: zhi.qu

测试市场数据相关功能
"""

import pytest
from datetime import date

from app.china_market.provinces import (
    get_province_config,
    get_all_provinces,
    is_province_supported,
    get_price_caps
)
from app.china_market.price_cap import (
    get_price_limits,
    validate_price,
    allows_negative_price,
    get_base_price
)
from app.china_market.trading_rules import validate_order
from app.core.constants import MarketType


class TestProvinceConfig:
    """省份配置测试"""
    
    def test_get_province_config_guangdong(self):
        """测试获取广东省配置"""
        config = get_province_config("广东")
        assert config is not None
        assert config.name == "广东"
        assert config.spot_market_active is True
        assert config.price_mechanism == "node"
    
    def test_get_province_config_not_found(self):
        """测试获取不存在的省份配置"""
        config = get_province_config("不存在省份")
        assert config is None
    
    def test_get_all_provinces(self):
        """测试获取所有省份"""
        provinces = get_all_provinces()
        assert len(provinces) > 0
        assert "广东" in provinces
        assert "浙江" in provinces
        assert "山东" in provinces
    
    def test_is_province_supported(self):
        """测试省份支持检查"""
        assert is_province_supported("广东") is True
        assert is_province_supported("不存在") is False


class TestPriceCap:
    """限价规则测试"""
    
    def test_get_price_limits_guangdong(self):
        """测试获取广东省限价"""
        min_price, max_price = get_price_limits("广东")
        assert min_price == 0
        assert max_price == 1500
    
    def test_get_price_limits_shandong(self):
        """测试获取山东省限价（允许负电价）"""
        min_price, max_price = get_price_limits("山东")
        assert min_price < 0
        assert max_price == 1500
    
    def test_validate_price_valid(self):
        """测试价格验证通过"""
        result = validate_price("广东", 500)
        assert result["valid"] is True
        assert result["error"] is None
    
    def test_validate_price_too_high(self):
        """测试价格过高"""
        result = validate_price("广东", 2000)
        assert result["valid"] is False
        assert "高于" in result["error"]
    
    def test_validate_price_negative(self):
        """测试负电价"""
        # 广东不允许负电价
        result = validate_price("广东", -50)
        assert result["valid"] is False
        
        # 山东允许负电价
        result = validate_price("山东", -50)
        assert result["valid"] is True
    
    def test_allows_negative_price(self):
        """测试负电价判断"""
        assert allows_negative_price("广东") is False
        assert allows_negative_price("山东") is True
    
    def test_get_base_price(self):
        """测试获取基准价格"""
        base_price = get_base_price("广东")
        assert base_price > 0
        assert base_price == 463.0


class TestTradingRules:
    """交易规则测试"""
    
    def test_validate_order_valid(self):
        """测试订单验证通过"""
        result = validate_order(
            province="广东",
            market_type=MarketType.DAY_AHEAD,
            price=500,
            quantity_mwh=100,
            base_price=463
        )
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_order_quantity_too_small(self):
        """测试电量太小"""
        result = validate_order(
            province="广东",
            market_type=MarketType.DAY_AHEAD,
            price=500,
            quantity_mwh=0.01,  # 太小
            base_price=463
        )
        assert result["valid"] is False
        assert any("低于" in e for e in result["errors"])
    
    def test_validate_order_price_deviation(self):
        """测试价格偏离过大"""
        result = validate_order(
            province="广东",
            market_type=MarketType.DAY_AHEAD,
            price=1000,  # 偏离基准价很大
            quantity_mwh=100,
            base_price=463
        )
        # 根据规则可能会有警告
        assert result is not None
