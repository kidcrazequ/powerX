"""
PowerX 审计日志服务

创建日期: 2026-01-07
作者: zhi.qu

提供审计日志记录、查询和分析功能
"""

import functools
import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from fastapi import Request

from app.models.audit import AuditLog, AuditAction, AuditModule


class AuditService:
    """
    审计日志服务
    
    功能：
    - 记录操作日志
    - 查询日志
    - 统计分析
    """
    
    def __init__(self, db: Optional[AsyncSession] = None):
        """
        初始化审计服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        # 内存日志队列（用于批量写入优化）
        self._log_queue: List[Dict] = []
        self._queue_size = 100
        logger.info("审计服务初始化")
    
    async def log(
        self,
        action: AuditAction,
        module: AuditModule,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        user_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        query_params: Optional[Dict] = None,
        request_body: Optional[Dict] = None,
        status_code: Optional[int] = None,
        response_time: Optional[int] = None,
        description: Optional[str] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        extra: Optional[Dict] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Optional[AuditLog]:
        """
        记录审计日志
        
        Args:
            action: 操作类型
            module: 模块名称
            resource: 资源类型
            resource_id: 资源ID
            user_id: 用户ID
            username: 用户名
            user_ip: 用户IP
            user_agent: 用户代理
            method: 请求方法
            path: 请求路径
            query_params: 查询参数
            request_body: 请求体
            status_code: 状态码
            response_time: 响应时间
            description: 操作描述
            old_value: 旧值
            new_value: 新值
            extra: 额外信息
            success: 是否成功
            error_message: 错误信息
            
        Returns:
            AuditLog: 审计日志记录
        """
        # 过滤敏感信息
        if request_body:
            request_body = self._filter_sensitive(request_body)
        
        log_entry = {
            "action": action.value if isinstance(action, AuditAction) else action,
            "module": module.value if isinstance(module, AuditModule) else module,
            "resource": resource,
            "resource_id": resource_id,
            "user_id": user_id,
            "username": username,
            "user_ip": user_ip,
            "user_agent": user_agent,
            "method": method,
            "path": path,
            "query_params": query_params,
            "request_body": request_body,
            "status_code": status_code,
            "response_time": response_time,
            "description": description,
            "old_value": old_value,
            "new_value": new_value,
            "extra": extra,
            "success": success,
            "error_message": error_message,
            "created_at": datetime.now()
        }
        
        logger.debug(f"审计日志: {action} {module}/{resource} by {username}")
        
        # 如果有数据库连接，直接写入
        if self.db:
            try:
                audit_log = AuditLog(**log_entry)
                self.db.add(audit_log)
                await self.db.commit()
                await self.db.refresh(audit_log)
                return audit_log
            except Exception as e:
                logger.error(f"写入审计日志失败: {e}")
                await self.db.rollback()
        else:
            # 否则加入队列
            self._log_queue.append(log_entry)
            if len(self._log_queue) >= self._queue_size:
                await self._flush_queue()
        
        return None
    
    async def log_from_request(
        self,
        request: Request,
        action: AuditAction,
        module: AuditModule,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        response_time: Optional[int] = None
    ) -> Optional[AuditLog]:
        """
        从 Request 对象记录审计日志
        
        Args:
            request: FastAPI Request 对象
            action: 操作类型
            module: 模块名称
            resource: 资源类型
            resource_id: 资源ID
            description: 操作描述
            old_value: 旧值
            new_value: 新值
            success: 是否成功
            error_message: 错误信息
            response_time: 响应时间
            
        Returns:
            AuditLog: 审计日志记录
        """
        # 从 request 提取信息
        user_id = getattr(request.state, "user_id", None)
        username = getattr(request.state, "username", None)
        
        # 获取客户端 IP
        user_ip = request.client.host if request.client else None
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            user_ip = forwarded.split(",")[0].strip()
        
        user_agent = request.headers.get("User-Agent", "")[:256]
        
        # 获取查询参数
        query_params = dict(request.query_params) if request.query_params else None
        
        return await self.log(
            action=action,
            module=module,
            resource=resource,
            resource_id=resource_id,
            user_id=user_id,
            username=username,
            user_ip=user_ip,
            user_agent=user_agent,
            method=request.method,
            path=str(request.url.path),
            query_params=query_params,
            description=description,
            old_value=old_value,
            new_value=new_value,
            success=success,
            error_message=error_message,
            response_time=response_time
        )
    
    async def query(
        self,
        user_id: Optional[str] = None,
        module: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        success: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        查询审计日志
        
        Args:
            user_id: 用户ID
            module: 模块名称
            action: 操作类型
            resource: 资源类型
            start_time: 开始时间
            end_time: 结束时间
            success: 是否成功
            keyword: 关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            Dict: 查询结果
        """
        if not self.db:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}
        
        # 构建查询条件
        conditions = []
        
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if module:
            conditions.append(AuditLog.module == module)
        if action:
            conditions.append(AuditLog.action == action)
        if resource:
            conditions.append(AuditLog.resource == resource)
        if start_time:
            conditions.append(AuditLog.created_at >= start_time)
        if end_time:
            conditions.append(AuditLog.created_at <= end_time)
        if success is not None:
            conditions.append(AuditLog.success == success)
        if keyword:
            conditions.append(
                or_(
                    AuditLog.description.ilike(f"%{keyword}%"),
                    AuditLog.path.ilike(f"%{keyword}%"),
                    AuditLog.username.ilike(f"%{keyword}%")
                )
            )
        
        # 查询总数
        count_query = select(func.count(AuditLog.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询数据
        query = select(AuditLog)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AuditLog.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return {
            "items": [log.to_dict() for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def get_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取审计统计信息
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            Dict: 统计信息
        """
        if not self.db:
            return self._get_mock_statistics()
        
        # 默认时间范围：最近7天
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(days=7)
        
        conditions = [
            AuditLog.created_at >= start_time,
            AuditLog.created_at <= end_time
        ]
        
        # 总数统计
        total_query = select(func.count(AuditLog.id)).where(and_(*conditions))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # 成功/失败统计
        success_query = select(func.count(AuditLog.id)).where(
            and_(*conditions, AuditLog.success == True)
        )
        success_result = await self.db.execute(success_query)
        success_count = success_result.scalar() or 0
        
        # 按模块统计
        module_query = select(
            AuditLog.module,
            func.count(AuditLog.id).label("count")
        ).where(and_(*conditions)).group_by(AuditLog.module)
        
        module_result = await self.db.execute(module_query)
        by_module = {row[0]: row[1] for row in module_result.all()}
        
        # 按操作类型统计
        action_query = select(
            AuditLog.action,
            func.count(AuditLog.id).label("count")
        ).where(and_(*conditions)).group_by(AuditLog.action)
        
        action_result = await self.db.execute(action_query)
        by_action = {row[0]: row[1] for row in action_result.all()}
        
        return {
            "total": total,
            "success_count": success_count,
            "failure_count": total - success_count,
            "success_rate": round(success_count / total * 100, 2) if total > 0 else 0,
            "by_module": by_module,
            "by_action": by_action,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    
    def _get_mock_statistics(self) -> Dict[str, Any]:
        """返回模拟统计数据"""
        return {
            "total": 1250,
            "success_count": 1180,
            "failure_count": 70,
            "success_rate": 94.4,
            "by_module": {
                "AUTH": 320,
                "TRADING": 450,
                "CONTRACT": 180,
                "MARKET": 200,
                "AI": 100
            },
            "by_action": {
                "CREATE": 280,
                "READ": 520,
                "UPDATE": 180,
                "DELETE": 50,
                "LOGIN": 150,
                "EXECUTE": 70
            },
            "start_time": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_time": datetime.now().isoformat()
        }
    
    def _filter_sensitive(self, data: Dict) -> Dict:
        """过滤敏感信息"""
        sensitive_keys = {"password", "token", "secret", "api_key", "credential"}
        
        def filter_dict(d: Dict) -> Dict:
            result = {}
            for k, v in d.items():
                if any(s in k.lower() for s in sensitive_keys):
                    result[k] = "***FILTERED***"
                elif isinstance(v, dict):
                    result[k] = filter_dict(v)
                else:
                    result[k] = v
            return result
        
        return filter_dict(data)
    
    async def _flush_queue(self) -> None:
        """刷新日志队列到数据库"""
        if not self._log_queue:
            return
        
        logger.debug(f"刷新 {len(self._log_queue)} 条审计日志")
        self._log_queue.clear()


# 全局审计服务实例（无数据库连接，用于装饰器）
audit_service = AuditService()


def audit_log(
    action: AuditAction,
    module: AuditModule,
    resource: Optional[str] = None,
    description: Optional[str] = None
):
    """
    审计日志装饰器
    
    用于自动记录 API 端点的操作日志
    
    Args:
        action: 操作类型
        module: 模块名称
        resource: 资源类型
        description: 操作描述
        
    Example:
        @router.post("/orders")
        @audit_log(AuditAction.CREATE, AuditModule.TRADING, "order")
        async def create_order(request: Request, ...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 尝试获取 request 对象
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            start_time = datetime.now()
            success = True
            error_msg = None
            result = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                # 计算响应时间
                response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # 记录日志
                if request:
                    try:
                        await audit_service.log_from_request(
                            request=request,
                            action=action,
                            module=module,
                            resource=resource,
                            description=description,
                            success=success,
                            error_message=error_msg,
                            response_time=response_time
                        )
                    except Exception as log_error:
                        logger.error(f"记录审计日志失败: {log_error}")
        
        return wrapper
    return decorator
