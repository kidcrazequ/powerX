"""
PowerX 审批流程数据模型

创建日期: 2026-01-07
作者: zhi.qu

定义审批流程相关的数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ApprovalStatus(str, enum.Enum):
    """审批状态"""
    PENDING = "PENDING"       # 待审批
    APPROVED = "APPROVED"     # 已批准
    REJECTED = "REJECTED"     # 已拒绝
    CANCELLED = "CANCELLED"   # 已取消


class ApprovalType(str, enum.Enum):
    """审批类型"""
    LARGE_TRADE = "LARGE_TRADE"      # 大额交易
    LIMIT_CHANGE = "LIMIT_CHANGE"    # 限额变更
    USER_ROLE = "USER_ROLE"          # 用户角色变更
    SYSTEM_CONFIG = "SYSTEM_CONFIG"  # 系统配置变更


class ApprovalFlow(Base):
    """审批流程定义"""
    
    __tablename__ = "approval_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 适用条件
    approval_type = Column(String(50), nullable=False)
    trigger_condition = Column(JSON, nullable=True)  # 触发条件
    
    # 审批配置
    approver_roles = Column(JSON, default=list)  # 可审批角色
    min_approvers = Column(Integer, default=1)   # 最少审批人数
    require_all = Column(Boolean, default=False)  # 是否需要所有人批准
    
    # 状态
    is_enabled = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ApprovalRequest(Base):
    """审批请求"""
    
    __tablename__ = "approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=False)
    
    # 申请人
    requester_id = Column(String, nullable=False, index=True)
    requester_name = Column(String(100), nullable=True)
    
    # 申请内容
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    request_data = Column(JSON, nullable=True)  # 请求详细数据
    
    # 状态
    status = Column(String(20), default=ApprovalStatus.PENDING.value, index=True)
    
    # 审批信息
    approvals = Column(JSON, default=list)  # [{approver_id, approved_at, comment}]
    current_step = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ApprovalRecord(Base):
    """审批记录"""
    
    __tablename__ = "approval_records"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=False)
    
    # 审批人
    approver_id = Column(String, nullable=False)
    approver_name = Column(String(100), nullable=True)
    
    # 审批结果
    action = Column(String(20), nullable=False)  # APPROVE / REJECT
    comment = Column(Text, nullable=True)
    
    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
