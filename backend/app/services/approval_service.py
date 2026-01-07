"""
PowerX 审批服务

创建日期: 2026-01-07
作者: zhi.qu

提供审批流程管理功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.models.approval import ApprovalFlow, ApprovalRequest, ApprovalRecord, ApprovalStatus


class ApprovalService:
    """审批服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_request(self, flow_id: int, requester_id: str, requester_name: str,
                            title: str, description: str = "", 
                            request_data: Optional[Dict] = None) -> ApprovalRequest:
        """创建审批请求"""
        request = ApprovalRequest(
            flow_id=flow_id, requester_id=requester_id, requester_name=requester_name,
            title=title, description=description, request_data=request_data or {}
        )
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        logger.info(f"创建审批请求: ID={request.id}, 标题={title}")
        return request
    
    async def get_pending_requests(self, approver_id: str = None) -> List[ApprovalRequest]:
        """获取待审批请求"""
        query = select(ApprovalRequest).where(ApprovalRequest.status == ApprovalStatus.PENDING.value)
        query = query.order_by(ApprovalRequest.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_my_requests(self, requester_id: str) -> List[ApprovalRequest]:
        """获取我的申请"""
        query = select(ApprovalRequest).where(ApprovalRequest.requester_id == requester_id)
        query = query.order_by(ApprovalRequest.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def approve(self, request_id: int, approver_id: str, approver_name: str,
                     comment: str = "") -> bool:
        """审批通过"""
        request = await self.db.get(ApprovalRequest, request_id)
        if not request or request.status != ApprovalStatus.PENDING.value:
            return False
        
        # 添加审批记录
        record = ApprovalRecord(
            request_id=request_id, approver_id=approver_id,
            approver_name=approver_name, action="APPROVE", comment=comment
        )
        self.db.add(record)
        
        # 更新请求状态
        request.status = ApprovalStatus.APPROVED.value
        request.completed_at = datetime.now()
        
        approvals = request.approvals or []
        approvals.append({"approver_id": approver_id, "approved_at": datetime.now().isoformat()})
        request.approvals = approvals
        
        await self.db.commit()
        logger.info(f"审批通过: 请求ID={request_id}, 审批人={approver_id}")
        return True
    
    async def reject(self, request_id: int, approver_id: str, approver_name: str,
                    comment: str = "") -> bool:
        """审批拒绝"""
        request = await self.db.get(ApprovalRequest, request_id)
        if not request or request.status != ApprovalStatus.PENDING.value:
            return False
        
        record = ApprovalRecord(
            request_id=request_id, approver_id=approver_id,
            approver_name=approver_name, action="REJECT", comment=comment
        )
        self.db.add(record)
        
        request.status = ApprovalStatus.REJECTED.value
        request.completed_at = datetime.now()
        
        await self.db.commit()
        logger.info(f"审批拒绝: 请求ID={request_id}, 审批人={approver_id}")
        return True
    
    async def cancel(self, request_id: int, requester_id: str) -> bool:
        """取消申请"""
        request = await self.db.get(ApprovalRequest, request_id)
        if not request or request.requester_id != requester_id:
            return False
        if request.status != ApprovalStatus.PENDING.value:
            return False
        
        request.status = ApprovalStatus.CANCELLED.value
        request.completed_at = datetime.now()
        
        await self.db.commit()
        logger.info(f"取消申请: 请求ID={request_id}")
        return True
    
    async def get_request_detail(self, request_id: int) -> Optional[Dict[str, Any]]:
        """获取请求详情"""
        request = await self.db.get(ApprovalRequest, request_id)
        if not request:
            return None
        
        # 获取审批记录
        query = select(ApprovalRecord).where(ApprovalRecord.request_id == request_id)
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return {
            "id": request.id,
            "title": request.title,
            "description": request.description,
            "requester_id": request.requester_id,
            "requester_name": request.requester_name,
            "status": request.status,
            "request_data": request.request_data,
            "created_at": request.created_at.isoformat() if request.created_at else None,
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
            "records": [{"approver_id": r.approver_id, "action": r.action,
                        "comment": r.comment, "created_at": r.created_at.isoformat() if r.created_at else None}
                       for r in records]
        }


def get_approval_service(db: AsyncSession) -> ApprovalService:
    return ApprovalService(db)
