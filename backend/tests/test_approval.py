"""
PowerX 审批服务测试
创建日期: 2026-01-07
作者: zhi.qu
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.approval_service import ApprovalService
from app.models.approval import ApprovalStatus


class TestApprovalService:
    """审批服务测试"""
    
    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.get = AsyncMock()
        return db
    
    @pytest.fixture
    def service(self, mock_db):
        return ApprovalService(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_request(self, service, mock_db):
        """测试创建审批请求"""
        result = await service.create_request(
            flow_id=1, requester_id="user1", requester_name="张三",
            title="测试审批", description="测试"
        )
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_approve_success(self, service, mock_db):
        """测试审批通过"""
        mock_request = MagicMock()
        mock_request.status = ApprovalStatus.PENDING.value
        mock_request.approvals = []
        mock_db.get = AsyncMock(return_value=mock_request)
        
        result = await service.approve(1, "admin1", "管理员", "同意")
        assert result is True
        assert mock_request.status == ApprovalStatus.APPROVED.value
    
    @pytest.mark.asyncio
    async def test_reject_success(self, service, mock_db):
        """测试审批拒绝"""
        mock_request = MagicMock()
        mock_request.status = ApprovalStatus.PENDING.value
        mock_db.get = AsyncMock(return_value=mock_request)
        
        result = await service.reject(1, "admin1", "管理员", "不同意")
        assert result is True
        assert mock_request.status == ApprovalStatus.REJECTED.value
