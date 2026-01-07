"""
PowerX 管理员 API

创建日期: 2026-01-07
作者: zhi.qu

用户管理、角色管理和系统配置
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from loguru import logger

from app.api.deps import get_current_user, get_db
from app.services.permission_service import PermissionService, permission_service, require_permission
from app.models.permission import PermissionType
from app.schemas.response import success_response

router = APIRouter()


# ============ 请求模型 ============

class CreateRoleRequest(BaseModel):
    """创建角色请求"""
    code: str = Field(..., min_length=2, max_length=32, description="角色代码")
    name: str = Field(..., min_length=2, max_length=64, description="角色名称")
    description: Optional[str] = Field(None, max_length=256, description="角色描述")
    permission_codes: Optional[List[str]] = Field(None, description="权限代码列表")


class UpdateRoleRequest(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=64, description="角色名称")
    description: Optional[str] = Field(None, max_length=256, description="角色描述")
    permission_codes: Optional[List[str]] = Field(None, description="权限代码列表")
    is_active: Optional[bool] = Field(None, description="是否启用")


class AssignRoleRequest(BaseModel):
    """分配角色请求"""
    user_id: str = Field(..., description="用户ID")
    role_code: str = Field(..., description="角色代码")


class UserRoleItem(BaseModel):
    """用户角色项"""
    id: str
    username: str
    email: Optional[str] = None
    roles: List[str]
    is_active: bool = True
    created_at: Optional[str] = None


# ============ 角色管理 API ============

@router.get("/roles")
async def list_roles(
    include_inactive: bool = Query(False, description="是否包含禁用的角色"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取角色列表
    """
    logger.info(f"获取角色列表: user={current_user}")
    
    service = PermissionService(db)
    roles = await service.list_roles(include_inactive)
    
    return success_response(data=roles)


@router.get("/roles/{role_id}")
async def get_role(
    role_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取角色详情
    """
    service = PermissionService(db)
    role = await service.get_role(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return success_response(data=role)


@router.post("/roles")
async def create_role(
    request: CreateRoleRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    创建角色
    """
    logger.info(f"创建角色: code={request.code}, name={request.name}")
    
    service = PermissionService(db)
    role = await service.create_role(
        code=request.code,
        name=request.name,
        description=request.description,
        permission_codes=request.permission_codes
    )
    
    return success_response(data=role, message="角色创建成功")


@router.put("/roles/{role_id}")
async def update_role(
    role_id: int,
    request: UpdateRoleRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新角色
    """
    logger.info(f"更新角色: role_id={role_id}")
    
    service = PermissionService(db)
    role = await service.update_role(
        role_id=role_id,
        name=request.name,
        description=request.description,
        permission_codes=request.permission_codes,
        is_active=request.is_active
    )
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return success_response(data=role, message="角色更新成功")


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    删除角色
    """
    logger.info(f"删除角色: role_id={role_id}")
    
    service = PermissionService(db)
    result = await service.delete_role(role_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return success_response(message="角色删除成功")


# ============ 权限管理 API ============

@router.get("/permissions")
async def list_permissions(
    module: Optional[str] = Query(None, description="模块筛选"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取权限列表
    """
    service = PermissionService(db)
    permissions = await service.list_permissions(module)
    
    return success_response(data=permissions)


@router.get("/permissions/modules")
async def get_permission_modules(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取权限模块列表
    """
    service = PermissionService(db)
    modules = await service.get_permission_modules()
    
    return success_response(data=modules)


# ============ 用户角色管理 API ============

@router.post("/users/roles")
async def assign_role_to_user(
    request: AssignRoleRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    为用户分配角色
    """
    logger.info(f"分配角色: user_id={request.user_id}, role={request.role_code}")
    
    service = PermissionService(db)
    await service.assign_role_to_user(request.user_id, request.role_code)
    
    return success_response(message="角色分配成功")


@router.delete("/users/{user_id}/roles/{role_code}")
async def remove_role_from_user(
    user_id: str,
    role_code: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    移除用户角色
    """
    logger.info(f"移除角色: user_id={user_id}, role={role_code}")
    
    service = PermissionService(db)
    await service.remove_role_from_user(user_id, role_code)
    
    return success_response(message="角色移除成功")


@router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取用户角色列表
    """
    service = PermissionService(db)
    roles = await service.get_user_roles(user_id)
    
    return success_response(data=roles)


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取用户权限列表
    """
    service = PermissionService(db)
    permissions = await service.get_user_permissions(user_id)
    
    return success_response(data=list(permissions))


# ============ 用户管理 API ============

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    role: Optional[str] = Query(None, description="角色筛选"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取用户列表
    """
    logger.info(f"获取用户列表: page={page}, keyword={keyword}")
    
    # 模拟用户数据
    mock_users = [
        {
            "id": "USER-001",
            "username": "admin",
            "email": "admin@powerx.com",
            "roles": ["super_admin"],
            "is_active": True,
            "created_at": "2026-01-01T00:00:00"
        },
        {
            "id": "USER-002",
            "username": "trader1",
            "email": "trader1@powerx.com",
            "roles": ["trader"],
            "is_active": True,
            "created_at": "2026-01-02T00:00:00"
        },
        {
            "id": "USER-003",
            "username": "analyst",
            "email": "analyst@powerx.com",
            "roles": ["analyst"],
            "is_active": True,
            "created_at": "2026-01-03T00:00:00"
        },
        {
            "id": "USER-004",
            "username": "risk_manager",
            "email": "risk@powerx.com",
            "roles": ["risk_manager"],
            "is_active": True,
            "created_at": "2026-01-04T00:00:00"
        }
    ]
    
    # 简单筛选
    if keyword:
        mock_users = [u for u in mock_users if keyword.lower() in u["username"].lower()]
    if role:
        mock_users = [u for u in mock_users if role in u["roles"]]
    
    return success_response(data={
        "items": mock_users,
        "total": len(mock_users),
        "page": page,
        "page_size": page_size
    })


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool = Query(..., description="是否启用"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新用户状态
    """
    logger.info(f"更新用户状态: user_id={user_id}, is_active={is_active}")
    
    return success_response(message=f"用户状态已{'启用' if is_active else '禁用'}")


# ============ 我的权限 API ============

@router.get("/me/roles")
async def get_my_roles(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取当前用户的角色列表
    """
    user_id = getattr(current_user, "id", None) or str(current_user)
    
    service = PermissionService(db)
    roles = await service.get_user_roles(user_id)
    
    return success_response(data=roles)


@router.get("/me/permissions")
async def get_my_permissions(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取当前用户的权限列表
    """
    user_id = getattr(current_user, "id", None) or str(current_user)
    
    service = PermissionService(db)
    permissions = await service.get_user_permissions(user_id)
    
    return success_response(data=list(permissions))
