"""
PowerX 交易模拟/回测 API

创建日期: 2026-01-07
作者: zhi.qu

提供回测和模拟交易相关的 RESTful API 端点
"""

from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import date
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.simulation_service import SimulationService
from app.models.simulation import SimulationSession, SimulationTrade
from app.schemas.response import APIResponse


router = APIRouter()


# ============ 请求/响应模型 ============

class StrategyInfo(BaseModel):
    """策略信息"""
    name: str
    description: str
    params: Dict[str, Any]


class BacktestCreate(BaseModel):
    """创建回测请求"""
    name: str = Field(..., description="回测名称", max_length=200)
    strategy_name: str = Field(..., description="策略名称")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    strategy_params: Optional[Dict[str, Any]] = Field(None, description="策略参数")
    initial_capital: float = Field(1000000.0, description="初始资金", gt=0)
    description: Optional[str] = Field(None, description="回测描述")


class SessionSummary(BaseModel):
    """回测会话摘要"""
    id: int
    name: str
    strategy_name: str
    status: str
    start_date: str
    end_date: str
    initial_capital: float
    total_return: Optional[float]
    win_rate: Optional[float]
    created_at: str


class SessionDetail(BaseModel):
    """回测会话详情"""
    id: int
    name: str
    description: Optional[str]
    simulation_type: str
    strategy_name: str
    strategy_params: Optional[Dict[str, Any]]
    start_date: str
    end_date: str
    initial_capital: float
    status: str
    progress: float
    final_capital: Optional[float]
    total_return: Optional[float]
    annual_return: Optional[float]
    max_drawdown: Optional[float]
    sharpe_ratio: Optional[float]
    win_rate: Optional[float]
    total_trades: Optional[int]
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]


class TradeRecord(BaseModel):
    """交易记录"""
    id: int
    trade_time: str
    direction: str
    price: float
    quantity: float
    amount: float
    commission: float
    profit: Optional[float]
    profit_rate: Optional[float]
    signal: Optional[str]


# ============ API 端点 ============

@router.get("/strategies", response_model=APIResponse[Dict[str, StrategyInfo]])
async def get_available_strategies(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取可用的交易策略列表
    
    返回所有可用策略及其参数说明
    """
    simulation_service = SimulationService(db)
    strategies = await simulation_service.get_available_strategies()
    return APIResponse.success_response(strategies)


@router.post("/backtest", response_model=APIResponse[SessionDetail])
async def create_backtest(
    request: BacktestCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建并执行回测任务
    
    创建新的回测会话并在后台执行
    """
    if request.start_date >= request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始日期必须早于结束日期"
        )
    
    simulation_service = SimulationService(db)
    
    try:
        session = await simulation_service.create_backtest(
            user_id=current_user.id,
            name=request.name,
            strategy_name=request.strategy_name,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy_params=request.strategy_params,
            initial_capital=request.initial_capital,
            description=request.description
        )
        
        # 后台执行回测
        background_tasks.add_task(
            run_backtest_task,
            session.id,
            db
        )
        
        return APIResponse.success_response(
            _session_to_detail(session),
            message="回测任务已创建，正在后台执行"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sessions", response_model=APIResponse[List[SessionSummary]])
async def get_user_sessions(
    status: Optional[str] = Query(None, description="状态过滤"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户的回测会话列表
    """
    simulation_service = SimulationService(db)
    sessions = await simulation_service.get_user_sessions(
        user_id=current_user.id,
        status=status,
        limit=limit
    )
    
    summaries = [
        SessionSummary(
            id=s.id,
            name=s.name,
            strategy_name=s.strategy_name,
            status=s.status,
            start_date=s.start_date.isoformat() if s.start_date else "",
            end_date=s.end_date.isoformat() if s.end_date else "",
            initial_capital=s.initial_capital,
            total_return=s.total_return,
            win_rate=s.win_rate,
            created_at=s.created_at.isoformat() if s.created_at else ""
        )
        for s in sessions
    ]
    
    return APIResponse.success_response(summaries)


@router.get("/sessions/{session_id}", response_model=APIResponse[SessionDetail])
async def get_session_detail(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取回测会话详情
    """
    simulation_service = SimulationService(db)
    session = await simulation_service.get_session_detail(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回测会话不存在"
        )
    
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此回测会话"
        )
    
    return APIResponse.success_response(_session_to_detail(session))


@router.get("/sessions/{session_id}/trades", response_model=APIResponse[List[TradeRecord]])
async def get_session_trades(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取回测会话的交易记录
    """
    simulation_service = SimulationService(db)
    
    # 验证权限
    session = await simulation_service.get_session_detail(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回测会话不存在"
        )
    
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此回测会话"
        )
    
    trades = await simulation_service.get_session_trades(session_id)
    
    trade_records = [
        TradeRecord(
            id=t.id,
            trade_time=t.trade_time.isoformat() if t.trade_time else "",
            direction=t.direction,
            price=t.price,
            quantity=t.quantity,
            amount=t.amount,
            commission=t.commission,
            profit=t.profit,
            profit_rate=t.profit_rate,
            signal=t.signal
        )
        for t in trades
    ]
    
    return APIResponse.success_response(trade_records)


@router.delete("/sessions/{session_id}", response_model=APIResponse[bool])
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    删除回测会话
    """
    simulation_service = SimulationService(db)
    
    # 验证权限
    session = await simulation_service.get_session_detail(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回测会话不存在"
        )
    
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此回测会话"
        )
    
    success = await simulation_service.delete_session(session_id)
    return APIResponse.success_response(success, message="回测会话已删除")


# ============ 辅助函数 ============

def _session_to_detail(session: SimulationSession) -> SessionDetail:
    """将会话模型转换为详情响应"""
    return SessionDetail(
        id=session.id,
        name=session.name,
        description=session.description,
        simulation_type=session.simulation_type,
        strategy_name=session.strategy_name,
        strategy_params=session.strategy_params,
        start_date=session.start_date.isoformat() if session.start_date else "",
        end_date=session.end_date.isoformat() if session.end_date else "",
        initial_capital=session.initial_capital,
        status=session.status,
        progress=session.progress or 0.0,
        final_capital=session.final_capital,
        total_return=session.total_return,
        annual_return=session.annual_return,
        max_drawdown=session.max_drawdown,
        sharpe_ratio=session.sharpe_ratio,
        win_rate=session.win_rate,
        total_trades=session.total_trades,
        result_data=session.result_data,
        error_message=session.error_message,
        created_at=session.created_at.isoformat() if session.created_at else "",
        started_at=session.started_at.isoformat() if session.started_at else None,
        completed_at=session.completed_at.isoformat() if session.completed_at else None
    )


async def run_backtest_task(session_id: int, db: AsyncSession):
    """后台执行回测任务"""
    from loguru import logger
    try:
        simulation_service = SimulationService(db)
        await simulation_service.run_backtest(session_id)
    except Exception as e:
        logger.error(f"回测任务执行失败 (session_id={session_id}): {e}")
