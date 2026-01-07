"""
PowerX 备份服务测试
创建日期: 2026-01-07
作者: zhi.qu
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from app.services.backup_service import BackupService


class TestBackupService:
    """备份服务测试"""
    
    @pytest.fixture
    def service(self, tmp_path):
        return BackupService(backup_dir=str(tmp_path / "backups"))
    
    @pytest.mark.asyncio
    async def test_create_backup(self, service):
        """测试创建备份"""
        result = await service.create_backup("test_backup")
        assert result["name"] == "test_backup"
        assert result["type"] == "full"
        assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_list_backups_empty(self, service):
        """测试列出空备份"""
        backups = await service.list_backups()
        assert backups == []
    
    @pytest.mark.asyncio
    async def test_list_backups_with_data(self, service):
        """测试列出备份"""
        await service.create_backup("backup1")
        await service.create_backup("backup2")
        
        backups = await service.list_backups()
        assert len(backups) == 2
    
    @pytest.mark.asyncio
    async def test_get_backup(self, service):
        """测试获取备份详情"""
        await service.create_backup("test_backup")
        
        backup = await service.get_backup("test_backup")
        assert backup is not None
        assert backup["name"] == "test_backup"
    
    @pytest.mark.asyncio
    async def test_get_backup_not_found(self, service):
        """测试获取不存在的备份"""
        backup = await service.get_backup("nonexistent")
        assert backup is None
    
    @pytest.mark.asyncio
    async def test_delete_backup(self, service):
        """测试删除备份"""
        await service.create_backup("to_delete")
        
        result = await service.delete_backup("to_delete")
        assert result is True
        
        backup = await service.get_backup("to_delete")
        assert backup is None
    
    @pytest.mark.asyncio
    async def test_delete_backup_not_found(self, service):
        """测试删除不存在的备份"""
        result = await service.delete_backup("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_storage_info(self, service):
        """测试获取存储信息"""
        info = await service.get_storage_info()
        
        assert "backup_count" in info
        assert "total_backup_size_mb" in info
        assert "disk_total_gb" in info
        assert "disk_usage_percent" in info
