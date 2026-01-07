"""
PowerX 通知服务测试
创建日期: 2026-01-07
作者: zhi.qu
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.notification_service import NotificationService


class TestNotificationService:
    """通知服务测试"""
    
    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.execute = AsyncMock()
        db.get = AsyncMock()
        db.delete = AsyncMock()
        return db
    
    @pytest.fixture
    def service(self, mock_db):
        return NotificationService(mock_db)
    
    def test_service_init_without_db(self):
        """测试无数据库初始化"""
        service = NotificationService()
        assert service.db is None
    
    @pytest.mark.asyncio
    async def test_send_notification_no_db(self):
        """测试无数据库时发送通知"""
        service = NotificationService()
        result = await service.send_notification("user1", "标题", "内容")
        assert result["total"] == 0
    
    @pytest.mark.asyncio
    async def test_add_channel(self, service, mock_db):
        """测试添加通知渠道"""
        mock_channel = MagicMock()
        mock_db.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))
        
        await service.add_channel("user1", "EMAIL", "测试邮箱", {"email": "test@test.com"})
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_delete_channel_success(self, service, mock_db):
        """测试删除通知渠道"""
        mock_channel = MagicMock()
        mock_db.get = AsyncMock(return_value=mock_channel)
        
        result = await service.delete_channel(1)
        assert result is True
        mock_db.delete.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_delete_channel_not_found(self, service, mock_db):
        """测试删除不存在的渠道"""
        mock_db.get = AsyncMock(return_value=None)
        
        result = await service.delete_channel(999)
        assert result is False
