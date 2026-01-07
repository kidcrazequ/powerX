"""
PowerX 合同服务

创建日期: 2026-01-07
作者: zhi.qu

合同管理业务逻辑
"""

import uuid
from datetime import date, datetime
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession


class ContractService:
    """合同服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # 模拟合同存储
        self._contracts: Dict[str, Dict] = {}
    
    async def create_contract(
        self,
        user_id: int,
        contract_type: str,
        counterparty: str,
        province: str,
        total_quantity_mwh: float,
        price: float,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        创建合同
        """
        contract_id = f"{contract_type[:2].upper()}{datetime.now().strftime('%Y')}{str(uuid.uuid4())[:6].upper()}"
        
        contract = {
            "id": contract_id,
            "user_id": user_id,
            "contract_type": contract_type,
            "counterparty": counterparty,
            "province": province,
            "total_quantity_mwh": total_quantity_mwh,
            "executed_quantity_mwh": 0,
            "price": price,
            "start_date": start_date,
            "end_date": end_date,
            "status": "PENDING" if start_date > date.today() else "ACTIVE",
            "created_at": datetime.now().isoformat()
        }
        
        self._contracts[contract_id] = contract
        return contract
    
    async def get_contracts(
        self,
        user_id: int,
        contract_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        获取合同列表
        """
        # 返回模拟数据
        mock_contracts = [
            {
                "id": "YL2026001",
                "contract_type": "YEARLY",
                "counterparty": "华能广东电厂",
                "province": "广东",
                "total_quantity_mwh": 50000,
                "executed_quantity_mwh": 8500,
                "price": 465.00,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "status": "ACTIVE",
                "created_at": "2025-12-15 15:20:00"
            },
            {
                "id": "MB2026002",
                "contract_type": "MONTHLY_BILATERAL",
                "counterparty": "大唐发电",
                "province": "广东",
                "total_quantity_mwh": 5000,
                "executed_quantity_mwh": 1200,
                "price": 478.50,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 1, 31),
                "status": "ACTIVE",
                "created_at": "2025-12-28 10:30:00"
            }
        ]
        
        # 合并实际创建的合同
        for contract in self._contracts.values():
            if contract["user_id"] == user_id:
                mock_contracts.append(contract)
        
        # 过滤
        if contract_type:
            mock_contracts = [c for c in mock_contracts if c["contract_type"] == contract_type]
        if status:
            mock_contracts = [c for c in mock_contracts if c["status"] == status]
        
        return mock_contracts
    
    async def get_contract(self, contract_id: str, user_id: int) -> Optional[Dict]:
        """
        获取合同详情
        """
        return self._contracts.get(contract_id)
    
    async def decompose_contract(
        self,
        contract_id: str,
        user_id: int,
        monthly_quantities: List[float]
    ) -> bool:
        """
        月度分解
        """
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError("合同不存在")
        
        if sum(monthly_quantities) != contract["total_quantity_mwh"]:
            raise ValueError("分解电量之和必须等于合同总电量")
        
        contract["monthly_plan"] = monthly_quantities
        return True
    
    async def get_execution_records(
        self,
        contract_id: str,
        user_id: int
    ) -> List[Dict]:
        """
        获取执行记录
        """
        # 返回模拟数据
        return [
            {"id": "1", "date": "2026-01-07", "quantity_mwh": 150, "price": 465.00, "status": "SETTLED"},
            {"id": "2", "date": "2026-01-06", "quantity_mwh": 145, "price": 465.00, "status": "SETTLED"},
            {"id": "3", "date": "2026-01-05", "quantity_mwh": 160, "price": 465.00, "status": "SETTLED"}
        ]
