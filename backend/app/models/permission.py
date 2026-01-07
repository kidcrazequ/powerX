"""
PowerX 权限管理模型

创建日期: 2026-01-07
作者: zhi.qu

用户角色和权限管理
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PermissionType(str, Enum):
    """权限类型"""
    # 交易权限
    TRADING_VIEW = "trading.view"
    TRADING_CREATE = "trading.create"
    TRADING_CANCEL = "trading.cancel"
    
    # 合同权限
    CONTRACT_VIEW = "contract.view"
    CONTRACT_CREATE = "contract.create"
    CONTRACT_EDIT = "contract.edit"
    CONTRACT_DELETE = "contract.delete"
    
    # 结算权限
    SETTLEMENT_VIEW = "settlement.view"
    SETTLEMENT_EXPORT = "settlement.export"
    
    # 市场数据权限
    MARKET_VIEW = "market.view"
    MARKET_REALTIME = "market.realtime"
    
    # AI 权限
    AI_CHAT = "ai.chat"
    AI_PREDICT = "ai.predict"
    AI_STRATEGY = "ai.strategy"
    AI_REPORT = "ai.report"
    
    # 报告权限
    REPORT_VIEW = "report.view"
    REPORT_CREATE = "report.create"
    REPORT_EXPORT = "report.export"
    
    # 管理权限
    ADMIN_USER = "admin.user"
    ADMIN_ROLE = "admin.role"
    ADMIN_AUDIT = "admin.audit"
    ADMIN_SYSTEM = "admin.system"


class RoleType(str, Enum):
    """预定义角色类型"""
    SUPER_ADMIN = "super_admin"     # 超级管理员
    ADMIN = "admin"                  # 管理员
    TRADER = "trader"                # 交易员
    ANALYST = "analyst"              # 分析师
    RISK_MANAGER = "risk_manager"    # 风控
    VIEWER = "viewer"                # 只读


# 角色-权限关联表
role_permission_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

# 用户-角色关联表
user_role_table = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(64), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, default=datetime.now)
)


class Permission(Base):
    """
    权限表
    
    定义系统中的所有权限
    """
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="权限代码")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="权限名称")
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="权限描述")
    module: Mapped[str] = mapped_column(String(32), nullable=False, comment="所属模块")
    
    # 关联
    roles = relationship("Role", secondary=role_permission_table, back_populates="permissions")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    def __repr__(self) -> str:
        return f"<Permission {self.code}>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "module": self.module
        }


class Role(Base):
    """
    角色表
    
    定义用户角色
    """
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, comment="角色代码")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="角色名称")
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="角色描述")
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否系统内置")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    
    # 关联
    permissions = relationship("Permission", secondary=role_permission_table, back_populates="roles")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self) -> str:
        return f"<Role {self.code}>"
    
    def to_dict(self, include_permissions: bool = False) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_permissions:
            result["permissions"] = [p.to_dict() for p in self.permissions]
        return result
    
    def has_permission(self, permission_code: str) -> bool:
        """检查角色是否拥有指定权限"""
        return any(p.code == permission_code for p in self.permissions)


# ============ 预定义角色权限 ============

DEFAULT_ROLE_PERMISSIONS = {
    RoleType.SUPER_ADMIN: list(PermissionType),  # 所有权限
    
    RoleType.ADMIN: [
        PermissionType.TRADING_VIEW,
        PermissionType.TRADING_CREATE,
        PermissionType.TRADING_CANCEL,
        PermissionType.CONTRACT_VIEW,
        PermissionType.CONTRACT_CREATE,
        PermissionType.CONTRACT_EDIT,
        PermissionType.SETTLEMENT_VIEW,
        PermissionType.SETTLEMENT_EXPORT,
        PermissionType.MARKET_VIEW,
        PermissionType.MARKET_REALTIME,
        PermissionType.AI_CHAT,
        PermissionType.AI_PREDICT,
        PermissionType.AI_STRATEGY,
        PermissionType.REPORT_VIEW,
        PermissionType.REPORT_CREATE,
        PermissionType.ADMIN_USER,
        PermissionType.ADMIN_AUDIT
    ],
    
    RoleType.TRADER: [
        PermissionType.TRADING_VIEW,
        PermissionType.TRADING_CREATE,
        PermissionType.TRADING_CANCEL,
        PermissionType.CONTRACT_VIEW,
        PermissionType.CONTRACT_CREATE,
        PermissionType.MARKET_VIEW,
        PermissionType.MARKET_REALTIME,
        PermissionType.AI_CHAT,
        PermissionType.AI_PREDICT,
        PermissionType.AI_STRATEGY
    ],
    
    RoleType.ANALYST: [
        PermissionType.TRADING_VIEW,
        PermissionType.CONTRACT_VIEW,
        PermissionType.SETTLEMENT_VIEW,
        PermissionType.MARKET_VIEW,
        PermissionType.MARKET_REALTIME,
        PermissionType.AI_CHAT,
        PermissionType.AI_PREDICT,
        PermissionType.AI_REPORT,
        PermissionType.REPORT_VIEW,
        PermissionType.REPORT_CREATE,
        PermissionType.REPORT_EXPORT
    ],
    
    RoleType.RISK_MANAGER: [
        PermissionType.TRADING_VIEW,
        PermissionType.CONTRACT_VIEW,
        PermissionType.SETTLEMENT_VIEW,
        PermissionType.MARKET_VIEW,
        PermissionType.MARKET_REALTIME,
        PermissionType.AI_PREDICT,
        PermissionType.REPORT_VIEW
    ],
    
    RoleType.VIEWER: [
        PermissionType.TRADING_VIEW,
        PermissionType.CONTRACT_VIEW,
        PermissionType.SETTLEMENT_VIEW,
        PermissionType.MARKET_VIEW,
        PermissionType.REPORT_VIEW
    ]
}
