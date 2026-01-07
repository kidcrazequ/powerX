"""
PowerX 交易模块测试

创建日期: 2026-01-07
作者: zhi.qu

测试交易相关功能
"""

import pytest
from datetime import date

from app.china_market.trading_rules import validate_order
from app.china_market.price_cap import validate_price


class TestOrderValidation:
    """订单验证测试"""
    
    def test_validate_order_valid(self):
        """测试有效订单"""
        result = validate_order(
            province="广东",
            market_type="DAY_AHEAD",
            price=485.0,
            quantity_mwh=100,
            base_price=463
        )
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_order_quantity_too_small(self):
        """测试电量过小"""
        result = validate_order(
            province="广东",
            market_type="DAY_AHEAD",
            price=485.0,
            quantity_mwh=0.01,  # 低于最小申报量
            base_price=463
        )
        assert result["valid"] is False
        assert any("低于" in e for e in result["errors"])
    
    def test_validate_order_quantity_too_large(self):
        """测试电量过大"""
        result = validate_order(
            province="广东",
            market_type="DAY_AHEAD",
            price=485.0,
            quantity_mwh=20000,  # 超过最大申报量
            base_price=463
        )
        assert result["valid"] is False
        assert any("超过" in e for e in result["errors"])
    
    def test_validate_order_price_deviation_warning(self):
        """测试价格偏离警告"""
        result = validate_order(
            province="广东",
            market_type="DAY_AHEAD",
            price=800.0,  # 偏离基准价较大
            quantity_mwh=100,
            base_price=463
        )
        # 应该有警告
        assert len(result["warnings"]) > 0
    
    def test_validate_price_guangdong(self):
        """测试广东价格验证"""
        # 正常价格
        result = validate_price("广东", 500)
        assert result["valid"] is True
        
        # 负价格（广东不允许）
        result = validate_price("广东", -50)
        assert result["valid"] is False
        
        # 超过上限
        result = validate_price("广东", 2000)
        assert result["valid"] is False
    
    def test_validate_price_shandong(self):
        """测试山东价格验证（允许负电价）"""
        # 正常价格
        result = validate_price("山东", 450)
        assert result["valid"] is True
        
        # 负价格（山东允许）
        result = validate_price("山东", -50)
        assert result["valid"] is True
        
        # 低于最低限价
        result = validate_price("山东", -150)
        assert result["valid"] is False


class TestTradingService:
    """交易服务测试"""
    
    @pytest.mark.asyncio
    async def test_create_order(self):
        """测试创建订单"""
        from app.services.trading_service import TradingService
        
        # 模拟数据库会话
        class MockDB:
            pass
        
        service = TradingService(MockDB())
        
        order = await service.create_order(
            user_id=1,
            province="广东",
            market_type="DAY_AHEAD",
            direction="BUY",
            price=485.0,
            quantity_mwh=100
        )
        
        assert order["id"] is not None
        assert order["province"] == "广东"
        assert order["market_type"] == "DAY_AHEAD"
        assert order["direction"] == "BUY"
        assert order["price"] == 485.0
    
    @pytest.mark.asyncio
    async def test_get_positions(self):
        """测试获取持仓"""
        from app.services.trading_service import TradingService
        
        class MockDB:
            pass
        
        service = TradingService(MockDB())
        positions = await service.get_positions(user_id=1)
        
        assert isinstance(positions, list)
        assert len(positions) > 0
