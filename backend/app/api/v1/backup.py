"""
PowerX 备份 API

创建日期: 2026-01-07
作者: zhi.qu

提供备份管理相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.services.backup_service import backup_service
from app.schemas.response import APIResponse


router = APIRouter()


class BackupCreate(BaseModel):
    """创建备份请求"""
    name: Optional[str] = Field(None, description="备份名称")
    backup_type: str = Field("full", description="备份类型")


@router.post("", response_model=APIResponse[Dict[str, Any]])
async def create_backup(
    request: BackupCreate,
    current_user = Depends(get_current_user)
):
    """创建备份"""
    result = await backup_service.create_backup(
        backup_name=request.name,
        backup_type=request.backup_type
    )
    return APIResponse.success_response(result, message="备份创建成功")


@router.get("", response_model=APIResponse[List[Dict[str, Any]]])
async def list_backups(
    current_user = Depends(get_current_user)
):
    """获取备份列表"""
    backups = await backup_service.list_backups()
    return APIResponse.success_response(backups)


@router.get("/storage", response_model=APIResponse[Dict[str, Any]])
async def get_storage_info(
    current_user = Depends(get_current_user)
):
    """获取存储信息"""
    info = await backup_service.get_storage_info()
    return APIResponse.success_response(info)


@router.get("/{backup_name}", response_model=APIResponse[Dict[str, Any]])
async def get_backup(
    backup_name: str,
    current_user = Depends(get_current_user)
):
    """获取备份详情"""
    backup = await backup_service.get_backup(backup_name)
    if not backup:
        raise HTTPException(status_code=404, detail="备份不存在")
    return APIResponse.success_response(backup)


@router.post("/{backup_name}/restore", response_model=APIResponse[Dict[str, Any]])
async def restore_backup(
    backup_name: str,
    current_user = Depends(get_current_user)
):
    """恢复备份"""
    result = await backup_service.restore_backup(backup_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return APIResponse.success_response(result)


@router.delete("/{backup_name}", response_model=APIResponse[bool])
async def delete_backup(
    backup_name: str,
    current_user = Depends(get_current_user)
):
    """删除备份"""
    success = await backup_service.delete_backup(backup_name)
    if not success:
        raise HTTPException(status_code=404, detail="备份不存在")
    return APIResponse.success_response(True, message="备份已删除")
