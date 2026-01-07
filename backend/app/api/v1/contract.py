"""
PowerX 合同管理 API

创建日期: 2026-01-07
作者: zhi.qu

合同相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from enum import Enum

from app.services.contract_service import ContractService
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# ============ 枚举类型 ============

class ContractType(str, Enum):
    YEARLY = "YEARLY"
    MONTHLY_BILATERAL = "MONTHLY_BILATERAL"
    MONTHLY_AUCTION = "MONTHLY_AUCTION"


class ContractStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# ============ 请求/响应模型 ============

class ContractCreateRequest(BaseModel):
    """创建合同请求"""
    contract_type: ContractType
    counterparty: str
    province: str
    total_quantity_mwh: float
    price: float
    start_date: date
    end_date: date


class ContractResponse(BaseModel):
    """合同响应"""
    id: str
    contract_type: str
    counterparty: str
    province: str
    total_quantity_mwh: float
    executed_quantity_mwh: float
    price: float
    start_date: str
    end_date: str
    status: str
    created_at: str


class MonthlyPlanRequest(BaseModel):
    """月度分解计划请求"""
    contract_id: str
    monthly_quantities: List[float]  # 12个月的分解电量


class ExecutionRecordResponse(BaseModel):
    """执行记录响应"""
    id: str
    date: str
    quantity_mwh: float
    price: float
    status: str


# ============ API 端点 ============

@router.post("/", response_model=ContractResponse)
async def create_contract(
    request: ContractCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建合同
    """
    service = ContractService(db)
    
    try:
        contract = await service.create_contract(
            user_id=current_user.id,
            contract_type=request.contract_type.value,
            counterparty=request.counterparty,
            province=request.province,
            total_quantity_mwh=request.total_quantity_mwh,
            price=request.price,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return ContractResponse(
            id=contract["id"],
            contract_type=contract["contract_type"],
            counterparty=contract["counterparty"],
            province=contract["province"],
            total_quantity_mwh=contract["total_quantity_mwh"],
            executed_quantity_mwh=contract.get("executed_quantity_mwh", 0),
            price=contract["price"],
            start_date=str(contract["start_date"]),
            end_date=str(contract["end_date"]),
            status=contract["status"],
            created_at=contract["created_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ContractResponse])
async def get_contracts(
    contract_type: Optional[ContractType] = None,
    status: Optional[ContractStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取合同列表
    """
    service = ContractService(db)
    
    contracts = await service.get_contracts(
        user_id=current_user.id,
        contract_type=contract_type.value if contract_type else None,
        status=status.value if status else None
    )
    
    return [
        ContractResponse(
            id=c["id"],
            contract_type=c["contract_type"],
            counterparty=c["counterparty"],
            province=c["province"],
            total_quantity_mwh=c["total_quantity_mwh"],
            executed_quantity_mwh=c.get("executed_quantity_mwh", 0),
            price=c["price"],
            start_date=str(c["start_date"]),
            end_date=str(c["end_date"]),
            status=c["status"],
            created_at=c["created_at"]
        )
        for c in contracts
    ]


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取合同详情
    """
    service = ContractService(db)
    contract = await service.get_contract(contract_id, current_user.id)
    
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    return ContractResponse(
        id=contract["id"],
        contract_type=contract["contract_type"],
        counterparty=contract["counterparty"],
        province=contract["province"],
        total_quantity_mwh=contract["total_quantity_mwh"],
        executed_quantity_mwh=contract.get("executed_quantity_mwh", 0),
        price=contract["price"],
        start_date=str(contract["start_date"]),
        end_date=str(contract["end_date"]),
        status=contract["status"],
        created_at=contract["created_at"]
    )


@router.post("/{contract_id}/decompose")
async def decompose_contract(
    contract_id: str,
    request: MonthlyPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    月度分解
    
    将年度合同分解到各月
    """
    if len(request.monthly_quantities) != 12:
        raise HTTPException(status_code=400, detail="必须提供12个月的分解电量")
    
    service = ContractService(db)
    
    try:
        await service.decompose_contract(
            contract_id=contract_id,
            user_id=current_user.id,
            monthly_quantities=request.monthly_quantities
        )
        return {"message": "分解计划已提交", "contract_id": contract_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{contract_id}/executions", response_model=List[ExecutionRecordResponse])
async def get_execution_records(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取执行记录
    """
    service = ContractService(db)
    records = await service.get_execution_records(contract_id, current_user.id)
    
    return [
        ExecutionRecordResponse(
            id=r["id"],
            date=r["date"],
            quantity_mwh=r["quantity_mwh"],
            price=r["price"],
            status=r["status"]
        )
        for r in records
    ]
