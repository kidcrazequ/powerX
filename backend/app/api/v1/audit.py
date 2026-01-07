"""
PowerX 审计日志 API

创建日期: 2026-01-07
作者: zhi.qu

审计日志查询和统计接口
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from loguru import logger

from app.api.deps import get_current_user, get_db
from app.services.audit_service import AuditService
from app.models.audit import AuditAction, AuditModule
from app.schemas.response import success_response, paginated_response

router = APIRouter()


# ============ 响应模型 ============

class AuditLogItem(BaseModel):
    """审计日志项"""
    id: int
    action: str
    module: str
    resource: Optional[str] = None
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    user_ip: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[int] = None
    description: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    created_at: Optional[str] = None


class AuditStatistics(BaseModel):
    """审计统计"""
    total: int
    success_count: int
    failure_count: int
    success_rate: float
    by_module: dict
    by_action: dict
    start_time: str
    end_time: str


# ============ API 端点 ============

@router.get("/logs")
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="用户ID"),
    module: Optional[str] = Query(None, description="模块名称"),
    action: Optional[str] = Query(None, description="操作类型"),
    resource: Optional[str] = Query(None, description="资源类型"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    success: Optional[bool] = Query(None, description="是否成功"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    查询审计日志
    
    支持多条件筛选和分页
    """
    logger.info(f"查询审计日志: user={current_user}, module={module}, action={action}")
    
    service = AuditService(db)
    
    result = await service.query(
        user_id=user_id,
        module=module,
        action=action,
        resource=resource,
        start_time=start_time,
        end_time=end_time,
        success=success,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    
    return paginated_response(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.get("/statistics")
async def get_audit_statistics(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取审计统计信息
    
    统计指定时间范围内的操作情况
    """
    logger.info(f"获取审计统计: start={start_time}, end={end_time}")
    
    service = AuditService(db)
    stats = await service.get_statistics(start_time, end_time)
    
    return success_response(data=stats)


@router.get("/modules")
async def get_audit_modules(
    current_user = Depends(get_current_user)
):
    """
    获取所有审计模块
    """
    modules = [{"value": m.value, "label": m.name} for m in AuditModule]
    return success_response(data=modules)


@router.get("/actions")
async def get_audit_actions(
    current_user = Depends(get_current_user)
):
    """
    获取所有审计操作类型
    """
    actions = [{"value": a.value, "label": a.name} for a in AuditAction]
    return success_response(data=actions)


@router.get("/recent")
async def get_recent_logs(
    limit: int = Query(10, ge=1, le=50, description="数量限制"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取最近的审计日志
    """
    service = AuditService(db)
    
    result = await service.query(page=1, page_size=limit)
    
    return success_response(data=result["items"])


@router.get("/my-activity")
async def get_my_activity(
    days: int = Query(7, ge=1, le=30, description="天数"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取当前用户的活动记录
    """
    service = AuditService(db)
    
    # 获取用户 ID
    user_id = getattr(current_user, "id", None) or str(current_user)
    
    start_time = datetime.now() - timedelta(days=days)
    
    result = await service.query(
        user_id=user_id,
        start_time=start_time,
        page_size=50
    )
    
    return success_response(data=result["items"])
