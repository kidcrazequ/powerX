"""
PowerX 期权交易 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.option_service import get_option_service

router = APIRouter(prefix="/options", tags=["期权交易"])


class CreateContractRequest(BaseModel):
    """创建合约请求"""
    name: str
    underlying: str
    option_type: str  # call/put
    option_style: str = "european"
    strike_price: float
    expiration_date: datetime
    contract_size: float = 1


class PlaceOrderRequest(BaseModel):
    """下单请求"""
    contract_id: str
    side: str  # buy/sell
    position_effect: str  # open/close
    quantity: float
    price: Optional[float] = None


class ExerciseRequest(BaseModel):
    """行权请求"""
    settlement_price: float


class ContractResponse(BaseModel):
    """合约响应"""
    contract_id: str
    name: str
    underlying: str
    option_type: str
    strike_price: float
    expiration_date: datetime
    premium: float
    is_active: bool


class OrderResponse(BaseModel):
    """订单响应"""
    order_id: str
    contract_id: str
    side: str
    position_effect: str
    quantity: float
    price: float
    total_premium: float
    status: str


class PositionResponse(BaseModel):
    """持仓响应"""
    contract_id: str
    side: str
    quantity: float
    avg_price: float
    unrealized_pnl: float


@router.post("/contracts", response_model=ContractResponse)
async def create_contract(
    request: CreateContractRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建期权合约"""
    service = get_option_service(db)
    
    contract = await service.create_contract(
        name=request.name,
        underlying=request.underlying,
        option_type=request.option_type,
        option_style=request.option_style,
        strike_price=request.strike_price,
        expiration_date=request.expiration_date,
        contract_size=request.contract_size
    )
    
    return ContractResponse(
        contract_id=contract.contract_id,
        name=contract.name,
        underlying=contract.underlying,
        option_type=contract.option_type,
        strike_price=contract.strike_price,
        expiration_date=contract.expiration_date,
        premium=contract.premium,
        is_active=contract.is_active
    )


@router.get("/contracts", response_model=List[ContractResponse])
async def list_contracts(
    underlying: Optional[str] = None,
    option_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取合约列表"""
    service = get_option_service(db)
    contracts = await service.list_contracts(underlying, option_type)
    
    return [
        ContractResponse(
            contract_id=c.contract_id,
            name=c.name,
            underlying=c.underlying,
            option_type=c.option_type,
            strike_price=c.strike_price,
            expiration_date=c.expiration_date,
            premium=c.premium,
            is_active=c.is_active
        )
        for c in contracts
    ]


@router.get("/contracts/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取合约详情"""
    service = get_option_service(db)
    contract = await service.get_contract(contract_id)
    
    if not contract:
        raise HTTPException(status_code=404, detail="合约不存在")
    
    return ContractResponse(
        contract_id=contract.contract_id,
        name=contract.name,
        underlying=contract.underlying,
        option_type=contract.option_type,
        strike_price=contract.strike_price,
        expiration_date=contract.expiration_date,
        premium=contract.premium,
        is_active=contract.is_active
    )


@router.post("/orders", response_model=OrderResponse)
async def place_order(
    request: PlaceOrderRequest,
    db: AsyncSession = Depends(get_db)
):
    """下单"""
    service = get_option_service(db)
    
    try:
        order = await service.place_order(
            user_id="user-001",
            contract_id=request.contract_id,
            side=request.side,
            position_effect=request.position_effect,
            quantity=request.quantity,
            price=request.price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return OrderResponse(
        order_id=order.order_id,
        contract_id=order.contract_id,
        side=order.side,
        position_effect=order.position_effect,
        quantity=order.quantity,
        price=order.price,
        total_premium=order.total_premium,
        status=order.status
    )


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    db: AsyncSession = Depends(get_db)
):
    """获取持仓"""
    service = get_option_service(db)
    positions = await service.get_positions(user_id="user-001")
    
    return [
        PositionResponse(
            contract_id=p.contract_id,
            side=p.side,
            quantity=p.quantity,
            avg_price=p.avg_price,
            unrealized_pnl=p.unrealized_pnl or 0
        )
        for p in positions
    ]


@router.post("/orders/{order_id}/exercise")
async def exercise_option(
    order_id: str,
    request: ExerciseRequest,
    db: AsyncSession = Depends(get_db)
):
    """行权"""
    service = get_option_service(db)
    
    try:
        result = await service.exercise_option(
            order_id=order_id,
            settlement_price=request.settlement_price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return result
