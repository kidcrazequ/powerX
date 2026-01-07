"""
PowerX 审批 API

创建日期: 2026-01-07
作者: zhi.qu

提供审批流程管理相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.approval_service import ApprovalService
from app.schemas.response import APIResponse


router = APIRouter()


class ApprovalRequestCreate(BaseModel):
    """创建审批请求"""
    flow_id: int = Field(1, description="审批流程ID")
    title: str = Field(..., description="申请标题")
    description: str = Field("", description="申请描述")
    request_data: Optional[Dict] = Field(None, description="请求数据")


class ApprovalAction(BaseModel):
    """审批操作"""
    comment: str = Field("", description="审批意见")


@router.post("/requests", response_model=APIResponse[Dict[str, Any]])
async def create_approval_request(
    request: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建审批请求"""
    service = ApprovalService(db)
    result = await service.create_request(
        flow_id=request.flow_id,
        requester_id=current_user.id,
        requester_name=current_user.username,
        title=request.title,
        description=request.description,
        request_data=request.request_data
    )
    return APIResponse.success_response({"id": result.id, "status": result.status}, message="申请提交成功")


@router.get("/requests/pending", response_model=APIResponse[List[Dict[str, Any]]])
async def get_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取待审批请求"""
    service = ApprovalService(db)
    requests = await service.get_pending_requests()
    return APIResponse.success_response([
        {"id": r.id, "title": r.title, "requester_name": r.requester_name,
         "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in requests
    ])


@router.get("/requests/my", response_model=APIResponse[List[Dict[str, Any]]])
async def get_my_requests(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取我的申请"""
    service = ApprovalService(db)
    requests = await service.get_my_requests(current_user.id)
    return APIResponse.success_response([
        {"id": r.id, "title": r.title, "status": r.status,
         "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in requests
    ])


@router.get("/requests/{request_id}", response_model=APIResponse[Dict[str, Any]])
async def get_request_detail(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取审批请求详情"""
    service = ApprovalService(db)
    detail = await service.get_request_detail(request_id)
    if not detail:
        raise HTTPException(status_code=404, detail="请求不存在")
    return APIResponse.success_response(detail)


@router.post("/requests/{request_id}/approve", response_model=APIResponse[bool])
async def approve_request(
    request_id: int,
    action: ApprovalAction,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """审批通过"""
    service = ApprovalService(db)
    success = await service.approve(request_id, current_user.id, current_user.username, action.comment)
    if not success:
        raise HTTPException(status_code=400, detail="审批失败")
    return APIResponse.success_response(True, message="审批通过")


@router.post("/requests/{request_id}/reject", response_model=APIResponse[bool])
async def reject_request(
    request_id: int,
    action: ApprovalAction,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """审批拒绝"""
    service = ApprovalService(db)
    success = await service.reject(request_id, current_user.id, current_user.username, action.comment)
    if not success:
        raise HTTPException(status_code=400, detail="拒绝失败")
    return APIResponse.success_response(True, message="审批已拒绝")


@router.post("/requests/{request_id}/cancel", response_model=APIResponse[bool])
async def cancel_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """取消申请"""
    service = ApprovalService(db)
    success = await service.cancel(request_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="取消失败")
    return APIResponse.success_response(True, message="申请已取消")
