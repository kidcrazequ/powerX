"""
PowerX 交易限额服务测试

创建日期: 2026-01-07
作者: zhi.qu
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from app.services.limit_service import LimitService, LimitCheckResult
from app.models.trading_limit import TradingLimit, LimitType


class TestLimitCheckResult:
    """限额检查结果测试"""
    
    def test_passed_result(self):
        """测试通过结果"""
        result = LimitCheckResult(passed=True, message="通过")
        
        assert result.passed is True
        assert result.message == "通过"
        assert result.limit_type is None
    
    def test_failed_result(self):
        """测试失败结果"""
        result = LimitCheckResult(
            passed=False,
            limit_type="SINGLE_QUANTITY",
            limit_value=100.0,
            attempted_value=150.0,
            message="超过单笔限额"
        )
        
        assert result.passed is False
        assert result.limit_type == "SINGLE_QUANTITY"
        assert result.limit_value == 100.0
        assert result.attempted_value == 150.0
    
    def test_to_dict(self):
        """测试转换为字典"""
        result = LimitCheckResult(
            passed=True,
            limit_type="DAILY_AMOUNT",
            limit_value=50000.0,
            current_usage=25000.0,
            attempted_value=10000.0,
            message="通过"
        )
        
        d = result.to_dict()
        
        assert d["passed"] is True
        assert d["limit_type"] == "DAILY_AMOUNT"
        assert d["limit_value"] == 50000.0
        assert d["current_usage"] == 25000.0


class TestLimitService:
    """限额服务测试"""
    
    @pytest.fixture
    def mock_db(self):
        """创建模拟数据库会话"""
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_db):
        """创建测试服务实例"""
        return LimitService(mock_db)
    
    def test_check_single_limit_quantity_pass(self, service):
        """测试单笔数量限额通过"""
        limit = MagicMock()
        limit.limit_type = LimitType.SINGLE_QUANTITY.value
        limit.limit_value = 100.0
        
        result = service._check_single_limit(limit, "BUY", 50.0, 25000.0, None)
        
        assert result.passed is True
    
    def test_check_single_limit_quantity_fail(self, service):
        """测试单笔数量限额失败"""
        limit = MagicMock()
        limit.limit_type = LimitType.SINGLE_QUANTITY.value
        limit.limit_value = 100.0
        
        result = service._check_single_limit(limit, "BUY", 150.0, 75000.0, None)
        
        assert result.passed is False
        assert result.attempted_value == 150.0
    
    def test_check_single_limit_amount_pass(self, service):
        """测试单笔金额限额通过"""
        limit = MagicMock()
        limit.limit_type = LimitType.SINGLE_AMOUNT.value
        limit.limit_value = 50000.0
        
        result = service._check_single_limit(limit, "BUY", 100.0, 45000.0, None)
        
        assert result.passed is True
    
    def test_check_single_limit_amount_fail(self, service):
        """测试单笔金额限额失败"""
        limit = MagicMock()
        limit.limit_type = LimitType.SINGLE_AMOUNT.value
        limit.limit_value = 50000.0
        
        result = service._check_single_limit(limit, "BUY", 100.0, 60000.0, None)
        
        assert result.passed is False
    
    def test_check_daily_quantity_pass(self, service):
        """测试每日数量限额通过"""
        limit = MagicMock()
        limit.limit_type = LimitType.DAILY_QUANTITY.value
        limit.limit_value = 500.0
        
        usage = MagicMock()
        usage.total_buy_quantity = 100.0
        usage.total_sell_quantity = 100.0
        
        result = service._check_single_limit(limit, "BUY", 100.0, 50000.0, usage)
        
        assert result.passed is True
    
    def test_check_daily_quantity_fail(self, service):
        """测试每日数量限额失败"""
        limit = MagicMock()
        limit.limit_type = LimitType.DAILY_QUANTITY.value
        limit.limit_value = 500.0
        
        usage = MagicMock()
        usage.total_buy_quantity = 300.0
        usage.total_sell_quantity = 150.0
        
        result = service._check_single_limit(limit, "BUY", 100.0, 50000.0, usage)
        
        assert result.passed is False
        assert result.current_usage == 450.0
