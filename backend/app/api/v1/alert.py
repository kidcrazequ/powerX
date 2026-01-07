"""
PowerX 预警 API

创建日期: 2026-01-07
作者: zhi.qu

预警规则管理和预警处理接口
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from loguru import logger

from app.api.deps import get_current_user, get_db
from app.services.alert_service import AlertService, alert_service
from app.models.alert import AlertType, AlertLevel, AlertStatus
from app.schemas.response import success_response, paginated_response

router = APIRouter()


# ============ 请求模型 ============

class CreateRuleRequest(BaseModel):
    """创建预警规则请求"""
    name: str = Field(..., min_length=2, max_length=64, description="规则名称")
    alert_type: str = Field(..., description="预警类型")
    level: str = Field(default="WARNING", description="预警级别")
    condition_type: str = Field(..., description="条件类型")
    condition_value: float = Field(..., description="条件阈值")
    condition_operator: str = Field(default=">=", description="比较运算符")
    province: Optional[str] = Field(None, description="适用省份")
    description: Optional[str] = Field(None, max_length=256, description="规则描述")
    notify_methods: Optional[List[str]] = Field(default=["websocket"], description="通知方式")


class UpdateRuleRequest(BaseModel):
    """更新预警规则请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=64, description="规则名称")
    level: Optional[str] = Field(None, description="预警级别")
    condition_value: Optional[float] = Field(None, description="条件阈值")
    condition_operator: Optional[str] = Field(None, description="比较运算符")
    description: Optional[str] = Field(None, max_length=256, description="规则描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class ResolveAlertRequest(BaseModel):
    """解决预警请求"""
    note: Optional[str] = Field(None, max_length=512, description="解决备注")


# ============ 预警规则 API ============

@router.get("/rules")
async def list_rules(
    alert_type: Optional[str] = Query(None, description="预警类型"),
    province: Optional[str] = Query(None, description="省份"),
    is_active: Optional[bool] = Query(True, description="是否启用"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取预警规则列表
    """
    logger.info(f"获取预警规则: type={alert_type}, province={province}")
    
    user_id = getattr(current_user, "id", None) or str(current_user)
    service = AlertService(db)
    
    rules = await service.list_rules(
        alert_type=alert_type,
        province=province,
        is_active=is_active,
        user_id=user_id
    )
    
    return success_response(data=rules)


@router.get("/rules/{rule_id}")
async def get_rule(
    rule_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取规则详情
    """
    service = AlertService(db)
    rule = await service.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    
    return success_response(data=rule)


@router.post("/rules")
async def create_rule(
    request: CreateRuleRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    创建预警规则
    """
    logger.info(f"创建预警规则: name={request.name}")
    
    user_id = getattr(current_user, "id", None) or str(current_user)
    service = AlertService(db)
    
    rule = await service.create_rule(
        name=request.name,
        alert_type=AlertType(request.alert_type),
        level=AlertLevel(request.level),
        condition_type=request.condition_type,
        condition_value=request.condition_value,
        condition_operator=request.condition_operator,
        province=request.province,
        description=request.description,
        notify_methods=request.notify_methods,
        user_id=user_id
    )
    
    return success_response(data=rule, message="规则创建成功")


@router.put("/rules/{rule_id}")
async def update_rule(
    rule_id: int,
    request: UpdateRuleRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新预警规则
    """
    logger.info(f"更新预警规则: rule_id={rule_id}")
    
    service = AlertService(db)
    rule = await service.update_rule(
        rule_id=rule_id,
        **request.model_dump(exclude_none=True)
    )
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    
    return success_response(data=rule, message="规则更新成功")


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    删除预警规则
    """
    logger.info(f"删除预警规则: rule_id={rule_id}")
    
    service = AlertService(db)
    result = await service.delete_rule(rule_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    
    return success_response(message="规则删除成功")


# ============ 预警记录 API ============

@router.get("/records")
async def list_alerts(
    status: Optional[str] = Query(None, description="状态"),
    level: Optional[str] = Query(None, description="级别"),
    alert_type: Optional[str] = Query(None, description="类型"),
    province: Optional[str] = Query(None, description="省份"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取预警记录列表
    """
    logger.info(f"获取预警记录: status={status}, level={level}")
    
    service = AlertService(db)
    result = await service.list_alerts(
        status=status,
        level=level,
        alert_type=alert_type,
        province=province,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size
    )
    
    return paginated_response(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.post("/records/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    确认预警
    """
    logger.info(f"确认预警: alert_id={alert_id}")
    
    user_id = getattr(current_user, "id", None) or str(current_user)
    service = AlertService(db)
    
    result = await service.acknowledge_alert(alert_id, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预警记录不存在"
        )
    
    return success_response(data=result, message="预警已确认")


@router.post("/records/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    request: ResolveAlertRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    解决预警
    """
    logger.info(f"解决预警: alert_id={alert_id}")
    
    user_id = getattr(current_user, "id", None) or str(current_user)
    service = AlertService(db)
    
    result = await service.resolve_alert(alert_id, user_id, request.note)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预警记录不存在"
        )
    
    return success_response(data=result, message="预警已解决")


# ============ 统计 API ============

@router.get("/statistics")
async def get_statistics(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取预警统计
    """
    service = AlertService(db)
    stats = await service.get_alert_statistics(start_time, end_time)
    
    return success_response(data=stats)


# ============ 预警类型 API ============

@router.get("/types")
async def get_alert_types(
    current_user = Depends(get_current_user)
):
    """
    获取预警类型列表
    """
    types = [
        {"value": t.value, "label": t.name.replace("_", " ").title()}
        for t in AlertType
    ]
    return success_response(data=types)


@router.get("/levels")
async def get_alert_levels(
    current_user = Depends(get_current_user)
):
    """
    获取预警级别列表
    """
    levels = [
        {"value": l.value, "label": l.name}
        for l in AlertLevel
    ]
    return success_response(data=levels)
