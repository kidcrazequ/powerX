"""
PowerX 权限管理服务

创建日期: 2026-01-07
作者: zhi.qu

提供用户角色和权限管理功能
"""

import functools
from typing import Any, Callable, Dict, List, Optional, Set
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from fastapi import HTTPException, status

from app.models.permission import (
    Permission, Role, PermissionType, RoleType,
    role_permission_table, user_role_table,
    DEFAULT_ROLE_PERMISSIONS
)


class PermissionService:
    """
    权限管理服务
    
    功能：
    - 角色管理
    - 权限管理
    - 用户角色分配
    - 权限检查
    """
    
    def __init__(self, db: Optional[AsyncSession] = None):
        """
        初始化权限服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        # 权限缓存 {user_id: set of permissions}
        self._permission_cache: Dict[str, Set[str]] = {}
        logger.info("权限服务初始化")
    
    # ============ 角色管理 ============
    
    async def create_role(
        self,
        code: str,
        name: str,
        description: Optional[str] = None,
        permission_codes: Optional[List[str]] = None,
        is_system: bool = False
    ) -> Dict[str, Any]:
        """
        创建角色
        
        Args:
            code: 角色代码
            name: 角色名称
            description: 角色描述
            permission_codes: 权限代码列表
            is_system: 是否系统内置
            
        Returns:
            Dict: 角色信息
        """
        logger.info(f"创建角色: code={code}, name={name}")
        
        if not self.db:
            return self._mock_create_role(code, name, description, permission_codes)
        
        # 检查是否已存在
        existing = await self.db.execute(
            select(Role).where(Role.code == code)
        )
        if existing.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"角色代码 {code} 已存在"
            )
        
        # 创建角色
        role = Role(
            code=code,
            name=name,
            description=description,
            is_system=is_system
        )
        
        # 添加权限
        if permission_codes:
            permissions = await self.db.execute(
                select(Permission).where(Permission.code.in_(permission_codes))
            )
            role.permissions = list(permissions.scalars().all())
        
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        
        return role.to_dict(include_permissions=True)
    
    async def get_role(self, role_id: int) -> Optional[Dict[str, Any]]:
        """获取角色详情"""
        if not self.db:
            return self._mock_get_role(role_id)
        
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        role = result.scalar()
        return role.to_dict(include_permissions=True) if role else None
    
    async def get_role_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """根据代码获取角色"""
        if not self.db:
            return self._mock_get_role_by_code(code)
        
        result = await self.db.execute(
            select(Role).where(Role.code == code)
        )
        role = result.scalar()
        return role.to_dict(include_permissions=True) if role else None
    
    async def list_roles(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """获取角色列表"""
        if not self.db:
            return self._mock_list_roles()
        
        query = select(Role)
        if not include_inactive:
            query = query.where(Role.is_active == True)
        
        result = await self.db.execute(query)
        roles = result.scalars().all()
        
        return [r.to_dict(include_permissions=True) for r in roles]
    
    async def update_role(
        self,
        role_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_codes: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """更新角色"""
        logger.info(f"更新角色: role_id={role_id}")
        
        if not self.db:
            return self._mock_update_role(role_id, name, description, permission_codes)
        
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        role = result.scalar()
        
        if not role:
            return None
        
        if role.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统内置角色不可修改"
            )
        
        if name:
            role.name = name
        if description:
            role.description = description
        if is_active is not None:
            role.is_active = is_active
        
        if permission_codes is not None:
            permissions = await self.db.execute(
                select(Permission).where(Permission.code.in_(permission_codes))
            )
            role.permissions = list(permissions.scalars().all())
        
        await self.db.commit()
        await self.db.refresh(role)
        
        # 清除相关用户的权限缓存
        self._clear_cache_by_role(role_id)
        
        return role.to_dict(include_permissions=True)
    
    async def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        logger.info(f"删除角色: role_id={role_id}")
        
        if not self.db:
            return True
        
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        role = result.scalar()
        
        if not role:
            return False
        
        if role.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统内置角色不可删除"
            )
        
        await self.db.delete(role)
        await self.db.commit()
        
        return True
    
    # ============ 权限管理 ============
    
    async def list_permissions(self, module: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取权限列表"""
        if not self.db:
            return self._mock_list_permissions(module)
        
        query = select(Permission)
        if module:
            query = query.where(Permission.module == module)
        
        result = await self.db.execute(query)
        permissions = result.scalars().all()
        
        return [p.to_dict() for p in permissions]
    
    async def get_permission_modules(self) -> List[Dict[str, str]]:
        """获取权限模块列表"""
        modules = set()
        for perm in PermissionType:
            module = perm.value.split(".")[0]
            modules.add(module)
        
        module_names = {
            "trading": "交易管理",
            "contract": "合同管理",
            "settlement": "结算管理",
            "market": "市场数据",
            "ai": "AI服务",
            "report": "报告管理",
            "admin": "系统管理"
        }
        
        return [
            {"code": m, "name": module_names.get(m, m)}
            for m in sorted(modules)
        ]
    
    # ============ 用户角色分配 ============
    
    async def assign_role_to_user(self, user_id: str, role_code: str) -> bool:
        """为用户分配角色"""
        logger.info(f"为用户分配角色: user_id={user_id}, role_code={role_code}")
        
        if not self.db:
            self._clear_user_cache(user_id)
            return True
        
        # 获取角色
        role_result = await self.db.execute(
            select(Role).where(Role.code == role_code, Role.is_active == True)
        )
        role = role_result.scalar()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色 {role_code} 不存在"
            )
        
        # 插入关联
        await self.db.execute(
            user_role_table.insert().values(user_id=user_id, role_id=role.id)
        )
        await self.db.commit()
        
        self._clear_user_cache(user_id)
        return True
    
    async def remove_role_from_user(self, user_id: str, role_code: str) -> bool:
        """移除用户角色"""
        logger.info(f"移除用户角色: user_id={user_id}, role_code={role_code}")
        
        if not self.db:
            self._clear_user_cache(user_id)
            return True
        
        role_result = await self.db.execute(
            select(Role).where(Role.code == role_code)
        )
        role = role_result.scalar()
        
        if not role:
            return False
        
        await self.db.execute(
            delete(user_role_table).where(
                user_role_table.c.user_id == user_id,
                user_role_table.c.role_id == role.id
            )
        )
        await self.db.commit()
        
        self._clear_user_cache(user_id)
        return True
    
    async def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户角色列表"""
        if not self.db:
            return self._mock_get_user_roles(user_id)
        
        query = select(Role).join(
            user_role_table,
            Role.id == user_role_table.c.role_id
        ).where(user_role_table.c.user_id == user_id)
        
        result = await self.db.execute(query)
        roles = result.scalars().all()
        
        return [r.to_dict() for r in roles]
    
    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """获取用户所有权限"""
        # 检查缓存
        if user_id in self._permission_cache:
            return self._permission_cache[user_id]
        
        if not self.db:
            permissions = self._mock_get_user_permissions(user_id)
        else:
            permissions = set()
            roles = await self.get_user_roles(user_id)
            
            for role_data in roles:
                role_result = await self.db.execute(
                    select(Role).where(Role.id == role_data["id"])
                )
                role = role_result.scalar()
                if role:
                    for perm in role.permissions:
                        permissions.add(perm.code)
        
        # 缓存
        self._permission_cache[user_id] = permissions
        return permissions
    
    async def check_permission(self, user_id: str, permission_code: str) -> bool:
        """检查用户是否拥有指定权限"""
        permissions = await self.get_user_permissions(user_id)
        return permission_code in permissions
    
    async def check_permissions(self, user_id: str, permission_codes: List[str], require_all: bool = True) -> bool:
        """
        检查用户是否拥有指定权限
        
        Args:
            user_id: 用户ID
            permission_codes: 权限代码列表
            require_all: True 表示需要全部权限，False 表示只需任一权限
        """
        permissions = await self.get_user_permissions(user_id)
        
        if require_all:
            return all(p in permissions for p in permission_codes)
        else:
            return any(p in permissions for p in permission_codes)
    
    # ============ 缓存管理 ============
    
    def _clear_user_cache(self, user_id: str) -> None:
        """清除用户权限缓存"""
        if user_id in self._permission_cache:
            del self._permission_cache[user_id]
    
    def _clear_cache_by_role(self, role_id: int) -> None:
        """清除指定角色相关用户的缓存"""
        # 简单实现：清除所有缓存
        self._permission_cache.clear()
    
    def clear_all_cache(self) -> None:
        """清除所有缓存"""
        self._permission_cache.clear()
    
    # ============ Mock 数据 ============
    
    def _mock_create_role(self, code: str, name: str, description: Optional[str], 
                          permission_codes: Optional[List[str]]) -> Dict[str, Any]:
        return {
            "id": 100,
            "code": code,
            "name": name,
            "description": description,
            "is_system": False,
            "is_active": True,
            "permissions": [{"code": p, "name": p} for p in (permission_codes or [])]
        }
    
    def _mock_get_role(self, role_id: int) -> Optional[Dict[str, Any]]:
        return {
            "id": role_id,
            "code": "trader",
            "name": "交易员",
            "description": "负责日常交易操作",
            "is_system": True,
            "is_active": True,
            "permissions": [
                {"code": "trading.view", "name": "查看交易"},
                {"code": "trading.create", "name": "创建交易"}
            ]
        }
    
    def _mock_get_role_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        roles = {
            "super_admin": {"id": 1, "name": "超级管理员"},
            "admin": {"id": 2, "name": "管理员"},
            "trader": {"id": 3, "name": "交易员"},
            "analyst": {"id": 4, "name": "分析师"},
            "viewer": {"id": 5, "name": "只读用户"}
        }
        if code in roles:
            return {
                "id": roles[code]["id"],
                "code": code,
                "name": roles[code]["name"],
                "is_system": True,
                "is_active": True
            }
        return None
    
    def _mock_list_roles(self) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "code": "super_admin", "name": "超级管理员", "is_system": True, "is_active": True},
            {"id": 2, "code": "admin", "name": "管理员", "is_system": True, "is_active": True},
            {"id": 3, "code": "trader", "name": "交易员", "is_system": True, "is_active": True},
            {"id": 4, "code": "analyst", "name": "分析师", "is_system": True, "is_active": True},
            {"id": 5, "code": "risk_manager", "name": "风控", "is_system": True, "is_active": True},
            {"id": 6, "code": "viewer", "name": "只读用户", "is_system": True, "is_active": True}
        ]
    
    def _mock_update_role(self, role_id: int, name: Optional[str], 
                          description: Optional[str], permission_codes: Optional[List[str]]) -> Dict[str, Any]:
        return {
            "id": role_id,
            "code": "custom_role",
            "name": name or "自定义角色",
            "description": description,
            "is_system": False,
            "is_active": True,
            "permissions": [{"code": p, "name": p} for p in (permission_codes or [])]
        }
    
    def _mock_list_permissions(self, module: Optional[str] = None) -> List[Dict[str, Any]]:
        permissions = []
        for perm in PermissionType:
            perm_module = perm.value.split(".")[0]
            if module is None or perm_module == module:
                permissions.append({
                    "code": perm.value,
                    "name": perm.value,
                    "module": perm_module
                })
        return permissions
    
    def _mock_get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        return [
            {"id": 3, "code": "trader", "name": "交易员", "is_system": True}
        ]
    
    def _mock_get_user_permissions(self, user_id: str) -> Set[str]:
        # 默认给予交易员权限
        return {p.value for p in DEFAULT_ROLE_PERMISSIONS.get(RoleType.TRADER, [])}


# 全局权限服务实例
permission_service = PermissionService()


def require_permission(*permission_codes: str, require_all: bool = True):
    """
    权限检查装饰器
    
    用于检查用户是否拥有指定权限
    
    Args:
        permission_codes: 权限代码
        require_all: True 表示需要全部权限，False 表示只需任一权限
        
    Example:
        @router.post("/orders")
        @require_permission("trading.create")
        async def create_order(request: Request, current_user = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 从 kwargs 获取 current_user
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未登录"
                )
            
            user_id = getattr(current_user, "id", None) or str(current_user)
            
            has_permission = await permission_service.check_permissions(
                user_id=user_id,
                permission_codes=list(permission_codes),
                require_all=require_all
            )
            
            if not has_permission:
                logger.warning(f"权限不足: user={user_id}, required={permission_codes}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
