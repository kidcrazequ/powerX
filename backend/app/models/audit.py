"""
PowerX 审计日志模型

创建日期: 2026-01-07
作者: zhi.qu

记录系统操作日志，用于追踪和审计
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditAction(str, Enum):
    """审计操作类型"""
    CREATE = "CREATE"       # 创建
    READ = "READ"           # 查询
    UPDATE = "UPDATE"       # 更新
    DELETE = "DELETE"       # 删除
    LOGIN = "LOGIN"         # 登录
    LOGOUT = "LOGOUT"       # 登出
    EXPORT = "EXPORT"       # 导出
    IMPORT = "IMPORT"       # 导入
    EXECUTE = "EXECUTE"     # 执行
    APPROVE = "APPROVE"     # 审批
    REJECT = "REJECT"       # 拒绝


class AuditModule(str, Enum):
    """审计模块"""
    AUTH = "AUTH"               # 认证
    TRADING = "TRADING"         # 交易
    CONTRACT = "CONTRACT"       # 合同
    SETTLEMENT = "SETTLEMENT"   # 结算
    MARKET = "MARKET"           # 市场
    AI = "AI"                   # AI服务
    REPORT = "REPORT"           # 报告
    ADMIN = "ADMIN"             # 管理
    SYSTEM = "SYSTEM"           # 系统


class AuditLog(Base):
    """
    审计日志表
    
    记录所有用户操作，支持查询和分析
    """
    __tablename__ = "audit_logs"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 操作信息
    action: Mapped[str] = mapped_column(String(32), nullable=False, comment="操作类型")
    module: Mapped[str] = mapped_column(String(32), nullable=False, comment="模块名称")
    resource: Mapped[str] = mapped_column(String(64), nullable=True, comment="资源类型")
    resource_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="资源ID")
    
    # 用户信息
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="用户ID")
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="用户名")
    user_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="用户IP")
    user_agent: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="用户代理")
    
    # 请求信息
    method: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, comment="请求方法")
    path: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="请求路径")
    query_params: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True, comment="查询参数")
    request_body: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True, comment="请求体")
    
    # 响应信息
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="状态码")
    response_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="响应时间(ms)")
    
    # 详情
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="操作描述")
    old_value: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True, comment="旧值")
    new_value: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True, comment="新值")
    extra: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True, comment="额外信息")
    
    # 结果
    success: Mapped[bool] = mapped_column(default=True, comment="是否成功")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="错误信息")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now, 
        nullable=False,
        comment="创建时间"
    )
    
    # 索引
    __table_args__ = (
        Index("idx_audit_user_id", "user_id"),
        Index("idx_audit_module", "module"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_created_at", "created_at"),
        Index("idx_audit_resource", "resource", "resource_id"),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog {self.id}: {self.action} {self.module}/{self.resource}>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "action": self.action,
            "module": self.module,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "username": self.username,
            "user_ip": self.user_ip,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "response_time": self.response_time,
            "description": self.description,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
