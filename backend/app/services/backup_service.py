"""
PowerX 备份服务

创建日期: 2026-01-07
作者: zhi.qu

提供数据备份和恢复功能
"""

import os
import shutil
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger


class BackupService:
    """备份服务"""
    
    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BackupService 初始化, 备份目录: {self.backup_dir}")
    
    async def create_backup(self, backup_name: str = None, backup_type: str = "full") -> Dict[str, Any]:
        """
        创建备份
        
        Args:
            backup_name: 备份名称
            backup_type: 备份类型 (full/incremental)
            
        Returns:
            备份结果
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not backup_name:
            backup_name = f"backup_{timestamp}"
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # 备份数据库
        db_backup = await self._backup_database(backup_path)
        
        # 备份配置文件
        config_backup = await self._backup_configs(backup_path)
        
        # 创建备份元数据
        metadata = {
            "name": backup_name,
            "type": backup_type,
            "created_at": datetime.now().isoformat(),
            "database": db_backup,
            "configs": config_backup,
            "size_mb": self._get_dir_size(backup_path)
        }
        
        # 保存元数据
        with open(backup_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"备份创建成功: {backup_name}")
        return metadata
    
    async def _backup_database(self, backup_path: Path) -> Dict[str, Any]:
        """备份数据库"""
        # SQLite 备份
        db_file = Path("./powerx.db")
        if db_file.exists():
            shutil.copy(db_file, backup_path / "powerx.db")
            return {"status": "success", "file": "powerx.db"}
        return {"status": "skipped", "reason": "数据库文件不存在"}
    
    async def _backup_configs(self, backup_path: Path) -> Dict[str, Any]:
        """备份配置文件"""
        config_dir = backup_path / "configs"
        config_dir.mkdir(exist_ok=True)
        
        config_files = [".env", "env.example"]
        backed_up = []
        
        for config_file in config_files:
            src = Path(f"./{config_file}")
            if src.exists():
                shutil.copy(src, config_dir / config_file)
                backed_up.append(config_file)
        
        return {"status": "success", "files": backed_up}
    
    def _get_dir_size(self, path: Path) -> float:
        """获取目录大小(MB)"""
        total = 0
        for file in path.rglob("*"):
            if file.is_file():
                total += file.stat().st_size
        return round(total / (1024 * 1024), 2)
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        backups = []
        
        for item in self.backup_dir.iterdir():
            if item.is_dir():
                metadata_file = item / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                        backups.append(metadata)
        
        # 按时间倒序
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return backups
    
    async def get_backup(self, backup_name: str) -> Optional[Dict[str, Any]]:
        """获取备份详情"""
        backup_path = self.backup_dir / backup_name
        metadata_file = backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file) as f:
            return json.load(f)
    
    async def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        恢复备份
        
        Args:
            backup_name: 备份名称
            
        Returns:
            恢复结果
        """
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            return {"success": False, "error": "备份不存在"}
        
        # 恢复数据库
        db_file = backup_path / "powerx.db"
        if db_file.exists():
            # 先备份当前数据库
            current_db = Path("./powerx.db")
            if current_db.exists():
                shutil.copy(current_db, current_db.with_suffix(".db.bak"))
            shutil.copy(db_file, current_db)
        
        logger.info(f"备份恢复成功: {backup_name}")
        return {
            "success": True,
            "message": f"备份 {backup_name} 已恢复",
            "restored_at": datetime.now().isoformat()
        }
    
    async def delete_backup(self, backup_name: str) -> bool:
        """删除备份"""
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            return False
        
        shutil.rmtree(backup_path)
        logger.info(f"备份已删除: {backup_name}")
        return True
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        total_size = self._get_dir_size(self.backup_dir)
        backup_count = len([d for d in self.backup_dir.iterdir() if d.is_dir()])
        
        # 磁盘空间
        disk_usage = shutil.disk_usage(self.backup_dir)
        
        return {
            "backup_count": backup_count,
            "total_backup_size_mb": total_size,
            "disk_total_gb": round(disk_usage.total / (1024**3), 2),
            "disk_used_gb": round(disk_usage.used / (1024**3), 2),
            "disk_free_gb": round(disk_usage.free / (1024**3), 2),
            "disk_usage_percent": round(disk_usage.used / disk_usage.total * 100, 1)
        }


# 单例实例
backup_service = BackupService()


def get_backup_service() -> BackupService:
    return backup_service
