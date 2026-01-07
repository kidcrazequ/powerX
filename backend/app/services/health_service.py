"""
PowerX 系统健康监控服务

创建日期: 2026-01-07
作者: zhi.qu

提供系统状态、数据库状态、API 指标等健康检查功能
"""

import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from collections import defaultdict
import asyncio


class HealthService:
    """系统健康服务"""
    
    def __init__(self):
        self._api_calls: List[Dict[str, Any]] = []
        self._start_time = datetime.now()
        self._max_history = 10000  # 最大保留的 API 调用记录数
        logger.info("HealthService 初始化完成")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            系统状态信息
        """
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 内存使用
        memory = psutil.virtual_memory()
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        
        # 运行时间
        uptime = datetime.now() - self._start_time
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split('.')[0],
            "cpu": {
                "usage_percent": cpu_percent,
                "cores": psutil.cpu_count(),
                "status": "normal" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent,
                "status": "normal" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round(disk.percent, 1),
                "status": "normal" if disk.percent < 80 else "warning" if disk.percent < 95 else "critical"
            }
        }
    
    async def get_db_status(self, db: AsyncSession) -> Dict[str, Any]:
        """
        获取数据库状态
        
        Args:
            db: 数据库会话
            
        Returns:
            数据库状态信息
        """
        try:
            start = time.time()
            # 执行简单查询测试连接
            await db.execute(text("SELECT 1"))
            latency = (time.time() - start) * 1000  # 毫秒
            
            return {
                "status": "connected",
                "latency_ms": round(latency, 2),
                "health": "normal" if latency < 100 else "warning" if latency < 500 else "critical"
            }
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return {
                "status": "disconnected",
                "error": str(e),
                "health": "critical"
            }
    
    def record_api_call(
        self,
        path: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None
    ):
        """
        记录 API 调用
        
        Args:
            path: 请求路径
            method: 请求方法
            status_code: 响应状态码
            response_time_ms: 响应时间(毫秒)
            user_id: 用户ID
        """
        self._api_calls.append({
            "timestamp": datetime.now(),
            "path": path,
            "method": method,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "user_id": user_id
        })
        
        # 限制历史记录数量
        if len(self._api_calls) > self._max_history:
            self._api_calls = self._api_calls[-self._max_history:]
    
    def get_api_metrics(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        获取 API 指标
        
        Args:
            hours: 统计时间范围(小时)
            
        Returns:
            API 指标
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_calls = [c for c in self._api_calls if c["timestamp"] >= cutoff]
        
        if not recent_calls:
            return {
                "time_range_hours": hours,
                "total_calls": 0,
                "avg_response_time_ms": 0,
                "error_rate": 0,
                "calls_per_minute": 0,
                "by_endpoint": {},
                "by_status": {},
                "by_method": {}
            }
        
        total_calls = len(recent_calls)
        total_response_time = sum(c["response_time_ms"] for c in recent_calls)
        error_calls = sum(1 for c in recent_calls if c["status_code"] >= 400)
        
        # 按端点统计
        by_endpoint = defaultdict(lambda: {"count": 0, "avg_time": 0, "total_time": 0})
        for c in recent_calls:
            ep = by_endpoint[c["path"]]
            ep["count"] += 1
            ep["total_time"] += c["response_time_ms"]
        
        for path, data in by_endpoint.items():
            data["avg_time"] = round(data["total_time"] / data["count"], 2)
            del data["total_time"]
        
        # 按状态码统计
        by_status = defaultdict(int)
        for c in recent_calls:
            by_status[str(c["status_code"])] += 1
        
        # 按方法统计
        by_method = defaultdict(int)
        for c in recent_calls:
            by_method[c["method"]] += 1
        
        # 计算每分钟调用数
        time_span = (datetime.now() - cutoff).total_seconds() / 60
        calls_per_minute = round(total_calls / time_span, 2) if time_span > 0 else 0
        
        return {
            "time_range_hours": hours,
            "total_calls": total_calls,
            "avg_response_time_ms": round(total_response_time / total_calls, 2),
            "error_rate": round(error_calls / total_calls * 100, 2),
            "error_count": error_calls,
            "calls_per_minute": calls_per_minute,
            "by_endpoint": dict(sorted(by_endpoint.items(), key=lambda x: x[1]["count"], reverse=True)[:20]),
            "by_status": dict(by_status),
            "by_method": dict(by_method)
        }
    
    def get_api_timeline(
        self,
        hours: int = 24,
        interval_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        获取 API 调用时间线
        
        Args:
            hours: 统计时间范围
            interval_minutes: 时间间隔(分钟)
            
        Returns:
            时间线数据
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_calls = [c for c in self._api_calls if c["timestamp"] >= cutoff]
        
        # 按时间间隔分组
        timeline = []
        current = cutoff
        interval = timedelta(minutes=interval_minutes)
        
        while current < datetime.now():
            next_time = current + interval
            period_calls = [
                c for c in recent_calls 
                if current <= c["timestamp"] < next_time
            ]
            
            if period_calls:
                avg_time = sum(c["response_time_ms"] for c in period_calls) / len(period_calls)
                errors = sum(1 for c in period_calls if c["status_code"] >= 400)
            else:
                avg_time = 0
                errors = 0
            
            timeline.append({
                "time": current.isoformat(),
                "count": len(period_calls),
                "avg_response_time_ms": round(avg_time, 2),
                "error_count": errors
            })
            
            current = next_time
        
        return timeline
    
    async def get_full_health_report(self, db: AsyncSession) -> Dict[str, Any]:
        """获取完整健康报告"""
        system_status = await self.get_system_status()
        db_status = await self.get_db_status(db)
        api_metrics = self.get_api_metrics(hours=1)
        
        # 计算总体健康评分
        health_score = 100
        issues = []
        
        # CPU 评估
        if system_status["cpu"]["status"] == "warning":
            health_score -= 10
            issues.append("CPU 使用率较高")
        elif system_status["cpu"]["status"] == "critical":
            health_score -= 25
            issues.append("CPU 使用率过高")
        
        # 内存评估
        if system_status["memory"]["status"] == "warning":
            health_score -= 10
            issues.append("内存使用率较高")
        elif system_status["memory"]["status"] == "critical":
            health_score -= 25
            issues.append("内存使用率过高")
        
        # 磁盘评估
        if system_status["disk"]["status"] == "warning":
            health_score -= 10
            issues.append("磁盘空间不足")
        elif system_status["disk"]["status"] == "critical":
            health_score -= 25
            issues.append("磁盘空间严重不足")
        
        # 数据库评估
        if db_status["health"] == "warning":
            health_score -= 15
            issues.append("数据库响应较慢")
        elif db_status["health"] == "critical":
            health_score -= 30
            issues.append("数据库连接异常")
        
        # API 错误率评估
        if api_metrics["error_rate"] > 5:
            health_score -= 15
            issues.append(f"API 错误率较高: {api_metrics['error_rate']}%")
        
        return {
            "overall_health_score": max(0, health_score),
            "overall_status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy",
            "issues": issues,
            "system": system_status,
            "database": db_status,
            "api": api_metrics,
            "generated_at": datetime.now().isoformat()
        }


# 单例实例
health_service = HealthService()


def get_health_service() -> HealthService:
    return health_service
