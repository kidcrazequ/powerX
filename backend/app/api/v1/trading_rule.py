"""
PowerX 交易规则 API

创建日期: 2026-01-07
作者: zhi.qu

提供交易规则相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.rule_engine import RuleEngine
from app.models.trading_rule import TradingRule, RuleExecution, RuleStatus, ActionType
from app.schemas.response import APIResponse


router = APIRouter()


# ============ 请求/响应模型 ============

class TradingRuleCreate(BaseModel):
    """创建交易规则请求"""
    name: str = Field(..., description="规则名称", max_length=200)
    description: Optional[str] = Field(None, description="规则描述")
    condition_expression: Dict[str, Any] = Field(..., description="条件表达式")
    action_type: str = Field(..., description="动作类型")
    action_params: Optional[Dict[str, Any]] = Field(None, description="动作参数")
    provinces: Optional[List[str]] = Field(None, description="适用省份")
    market_types: Optional[List[str]] = Field(None, description="适用市场类型")
    priority: int = Field(0, description="优先级")
    max_executions_per_day: int = Field(10, ge=1, le=1000, description="每日最大执行次数")
    min_interval_seconds: int = Field(60, ge=0, description="最小执行间隔(秒)")


class TradingRuleUpdate(BaseModel):
    """更新交易规则请求"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    condition_expression: Optional[Dict[str, Any]] = None
    action_type: Optional[str] = None
    action_params: Optional[Dict[str, Any]] = None
    provinces: Optional[List[str]] = None
    market_types: Optional[List[str]] = None
    priority: Optional[int] = None
    max_executions_per_day: Optional[int] = None
    min_interval_seconds: Optional[int] = None


class TradingRuleResponse(BaseModel):
    """交易规则响应"""
    id: int
    user_id: str
    name: str
    description: Optional[str]
    status: str
    priority: int
    condition_expression: Dict[str, Any]
    action_type: str
    action_params: Optional[Dict[str, Any]]
    provinces: Optional[List[str]]
    market_types: Optional[List[str]]
    max_executions_per_day: int
    min_interval_seconds: int
    execution_count: int
    today_execution_count: int
    last_executed_at: Optional[str]
    created_at: str
    updated_at: Optional[str]


class RuleExecutionResponse(BaseModel):
    """规则执行记录响应"""
    id: int
    rule_id: int
    executed_at: str
    action_executed: Optional[str]
    success: bool
    action_result: Optional[Dict[str, Any]]
    error_message: Optional[str]


# ============ API 端点 ============

@router.post("", response_model=APIResponse[TradingRuleResponse])
async def create_trading_rule(
    request: TradingRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建交易规则
    
    条件表达式示例:
    ```json
    {
        "operator": "AND",
        "conditions": [
            {"field": "price", "op": ">", "value": 500},
            {"field": "province", "op": "==", "value": "广东"}
        ]
    }
    ```
    """
    engine = RuleEngine(db)
    
    try:
        rule = await engine.create_rule(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            condition_expression=request.condition_expression,
            action_type=request.action_type,
            action_params=request.action_params,
            provinces=request.provinces,
            market_types=request.market_types,
            priority=request.priority,
            max_executions_per_day=request.max_executions_per_day,
            min_interval_seconds=request.min_interval_seconds
        )
        
        return APIResponse.success_response(
            _rule_to_response(rule),
            message="交易规则创建成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=APIResponse[List[TradingRuleResponse]])
async def get_trading_rules(
    status_filter: Optional[str] = Query(None, alias="status", description="状态过滤"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户的交易规则列表
    """
    engine = RuleEngine(db)
    rules = await engine.get_user_rules(
        user_id=current_user.id,
        status=status_filter,
        limit=limit
    )
    
    return APIResponse.success_response([
        _rule_to_response(rule) for rule in rules
    ])


@router.get("/action-types", response_model=APIResponse[List[Dict[str, str]]])
async def get_action_types(
    current_user = Depends(get_current_user)
):
    """
    获取支持的动作类型列表
    """
    types = [
        {"value": ActionType.PLACE_ORDER.value, "label": "下单", "description": "创建交易订单"},
        {"value": ActionType.SEND_ALERT.value, "label": "发送预警", "description": "发送预警通知"},
        {"value": ActionType.CANCEL_ORDER.value, "label": "取消订单", "description": "取消指定订单"},
        {"value": ActionType.ADJUST_POSITION.value, "label": "调整仓位", "description": "调整持仓"},
        {"value": ActionType.EXECUTE_STRATEGY.value, "label": "执行策略", "description": "执行交易策略"},
    ]
    return APIResponse.success_response(types)


@router.get("/{rule_id}", response_model=APIResponse[TradingRuleResponse])
async def get_trading_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取交易规则详情
    """
    engine = RuleEngine(db)
    rule = await engine.get_rule_by_id(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    
    if rule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此规则"
        )
    
    return APIResponse.success_response(_rule_to_response(rule))


@router.put("/{rule_id}/status", response_model=APIResponse[TradingRuleResponse])
async def update_rule_status(
    rule_id: int,
    new_status: str = Query(..., description="新状态 (ACTIVE/INACTIVE/PAUSED)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新规则状态（启用/禁用）
    """
    engine = RuleEngine(db)
    
    # 验证权限
    rule = await engine.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    
    if rule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此规则"
        )
    
    # 验证状态值
    valid_statuses = [s.value for s in RuleStatus]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效状态，可选值: {valid_statuses}"
        )
    
    updated_rule = await engine.update_rule_status(rule_id, new_status)
    return APIResponse.success_response(
        _rule_to_response(updated_rule),
        message=f"规则状态已更新为 {new_status}"
    )


@router.delete("/{rule_id}", response_model=APIResponse[bool])
async def delete_trading_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    删除交易规则
    """
    engine = RuleEngine(db)
    
    # 验证权限
    rule = await engine.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    
    if rule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此规则"
        )
    
    success = await engine.delete_rule(rule_id)
    return APIResponse.success_response(True, message="规则已删除")


@router.get("/{rule_id}/executions", response_model=APIResponse[List[RuleExecutionResponse]])
async def get_rule_executions(
    rule_id: int,
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取规则执行历史
    """
    engine = RuleEngine(db)
    
    # 验证权限
    rule = await engine.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    
    if rule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此规则"
        )
    
    executions = await engine.get_rule_executions(rule_id, limit)
    
    return APIResponse.success_response([
        RuleExecutionResponse(
            id=exe.id,
            rule_id=exe.rule_id,
            executed_at=exe.executed_at.isoformat() if exe.executed_at else "",
            action_executed=exe.action_executed,
            success=exe.success,
            action_result=exe.action_result,
            error_message=exe.error_message
        )
        for exe in executions
    ])


@router.post("/test-expression", response_model=APIResponse[Dict[str, Any]])
async def test_condition_expression(
    expression: Dict[str, Any],
    test_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """
    测试条件表达式
    
    用于验证条件表达式是否正确配置
    """
    from app.services.rule_engine import RuleParser
    
    try:
        result = RuleParser.evaluate_expression(expression, test_data)
        return APIResponse.success_response({
            "expression": expression,
            "test_data": test_data,
            "result": result
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"表达式评估错误: {str(e)}"
        )


# ============ 辅助函数 ============

def _rule_to_response(rule: TradingRule) -> TradingRuleResponse:
    """将规则模型转换为响应"""
    return TradingRuleResponse(
        id=rule.id,
        user_id=rule.user_id,
        name=rule.name,
        description=rule.description,
        status=rule.status,
        priority=rule.priority,
        condition_expression=rule.condition_expression,
        action_type=rule.action_type,
        action_params=rule.action_params,
        provinces=rule.provinces,
        market_types=rule.market_types,
        max_executions_per_day=rule.max_executions_per_day,
        min_interval_seconds=rule.min_interval_seconds,
        execution_count=rule.execution_count,
        today_execution_count=rule.today_execution_count,
        last_executed_at=rule.last_executed_at.isoformat() if rule.last_executed_at else None,
        created_at=rule.created_at.isoformat() if rule.created_at else "",
        updated_at=rule.updated_at.isoformat() if rule.updated_at else None
    )
