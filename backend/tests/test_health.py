"""
PowerX 系统健康服务测试

创建日期: 2026-01-07
作者: zhi.qu
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.health_service import HealthService, health_service


class TestHealthService:
    """系统健康服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return HealthService()
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, service):
        """测试获取系统状态"""
        with patch('psutil.cpu_percent', return_value=45.0):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value = MagicMock(
                    total=16 * 1024**3,
                    used=8 * 1024**3,
                    available=8 * 1024**3,
                    percent=50.0
                )
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value = MagicMock(
                        total=500 * 1024**3,
                        used=200 * 1024**3,
                        free=300 * 1024**3,
                        percent=40.0
                    )
                    
                    result = await service.get_system_status()
        
        assert result["status"] == "healthy"
        assert "cpu" in result
        assert "memory" in result
        assert "disk" in result
        assert result["cpu"]["usage_percent"] == 45.0
        assert result["memory"]["percent"] == 50.0
    
    def test_record_api_call(self, service):
        """测试记录 API 调用"""
        service.record_api_call(
            path="/api/v1/test",
            method="GET",
            status_code=200,
            response_time_ms=50.0,
            user_id="user1"
        )
        
        assert len(service._api_calls) == 1
        assert service._api_calls[0]["path"] == "/api/v1/test"
        assert service._api_calls[0]["status_code"] == 200
    
    def test_get_api_metrics_empty(self, service):
        """测试空 API 指标"""
        metrics = service.get_api_metrics(hours=1)
        
        assert metrics["total_calls"] == 0
        assert metrics["avg_response_time_ms"] == 0
        assert metrics["error_rate"] == 0
    
    def test_get_api_metrics_with_data(self, service):
        """测试有数据的 API 指标"""
        # 添加一些测试数据
        for i in range(10):
            service.record_api_call(
                path=f"/api/v1/test{i % 3}",
                method="GET",
                status_code=200 if i < 8 else 500,
                response_time_ms=50.0 + i * 5,
                user_id="user1"
            )
        
        metrics = service.get_api_metrics(hours=1)
        
        assert metrics["total_calls"] == 10
        assert metrics["error_count"] == 2
        assert metrics["error_rate"] == 20.0
        assert metrics["avg_response_time_ms"] > 0
    
    def test_get_api_timeline(self, service):
        """测试 API 时间线"""
        # 添加测试数据
        for i in range(5):
            service.record_api_call(
                path="/api/v1/test",
                method="GET",
                status_code=200,
                response_time_ms=50.0
            )
        
        timeline = service.get_api_timeline(hours=1, interval_minutes=15)
        
        assert isinstance(timeline, list)
        assert len(timeline) > 0


class TestHealthServiceSingleton:
    """测试单例实例"""
    
    def test_singleton_instance(self):
        """测试单例实例"""
        assert health_service is not None
        assert isinstance(health_service, HealthService)
