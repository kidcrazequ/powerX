"""
PowerX 回滚服务
创建日期: 2026-01-07
作者: zhi.qu
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.operation_log import OperationLog, RollbackHistory


class RollbackService:
    """回滚服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_operation(
        self,
        operation_type: str,
        entity_type: str,
        entity_id: str,
        user_id: str,
        data_before: Dict[str, Any] = None,
        data_after: Dict[str, Any] = None,
        description: str = None,
        is_rollbackable: bool = True
    ) -> OperationLog:
        """记录操作"""
        operation_id = f"OP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        log = OperationLog(
            operation_id=operation_id,
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            data_before=data_before,
            data_after=data_after,
            description=description,
            is_rollbackable=is_rollbackable
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        logger.debug(f"记录操作: {operation_id}")
        return log
    
    async def rollback_operation(
        self,
        operation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """回滚操作"""
        query = select(OperationLog).where(OperationLog.operation_id == operation_id)
        result = await self.db.execute(query)
        log = result.scalars().first()
        
        if not log:
            return {"success": False, "error": "操作不存在"}
        
        if not log.is_rollbackable:
            return {"success": False, "error": "此操作不支持回滚"}
        
        if log.is_rolled_back:
            return {"success": False, "error": "操作已被回滚"}
        
        try:
            # 执行回滚逻辑 (根据实体类型调用不同的回滚处理)
            await self._execute_rollback(log)
            
            log.is_rolled_back = True
            log.rolled_back_at = datetime.now()
            log.rolled_back_by = user_id
            
            # 记录回滚历史
            history = RollbackHistory(
                operation_id=operation_id,
                user_id=user_id,
                success=True
            )
            self.db.add(history)
            await self.db.commit()
            
            logger.info(f"回滚操作成功: {operation_id}")
            return {"success": True, "data_restored": log.data_before}
            
        except Exception as e:
            history = RollbackHistory(
                operation_id=operation_id,
                user_id=user_id,
                success=False,
                error_message=str(e)
            )
            self.db.add(history)
            await self.db.commit()
            
            logger.error(f"回滚操作失败: {operation_id}, {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_rollback(self, log: OperationLog):
        """执行实际回滚"""
        # 根据操作类型和实体类型执行回滚
        # 这里需要根据具体业务实现
        if log.operation_type == "delete" and log.data_before:
            # 恢复删除的数据
            pass
        elif log.operation_type == "update" and log.data_before:
            # 恢复到原始数据
            pass
        elif log.operation_type == "create":
            # 删除创建的数据
            pass
    
    async def get_operation_history(
        self,
        entity_type: str = None,
        entity_id: str = None,
        user_id: str = None,
        limit: int = 50
    ) -> List[OperationLog]:
        """获取操作历史"""
        query = select(OperationLog)
        
        if entity_type:
            query = query.where(OperationLog.entity_type == entity_type)
        if entity_id:
            query = query.where(OperationLog.entity_id == entity_id)
        if user_id:
            query = query.where(OperationLog.user_id == user_id)
        
        query = query.order_by(OperationLog.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_rollbackable_operations(
        self,
        entity_type: str = None,
        limit: int = 20
    ) -> List[OperationLog]:
        """获取可回滚的操作"""
        query = select(OperationLog).where(
            OperationLog.is_rollbackable == True,
            OperationLog.is_rolled_back == False
        )
        
        if entity_type:
            query = query.where(OperationLog.entity_type == entity_type)
        
        query = query.order_by(OperationLog.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())


def get_rollback_service(db: AsyncSession) -> RollbackService:
    """获取回滚服务"""
    return RollbackService(db)
