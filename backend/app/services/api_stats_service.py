"""
PowerX API 统计服务
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger


class APIStatsService:
    """API 统计服务"""
    
    def __init__(self):
        self._calls: List[Dict] = []
        self._max_records = 50000
        logger.info("APIStatsService 初始化完成")
    
    def record_call(self, path: str, method: str, status_code: int, 
                   response_time_ms: float, user_id: str = None):
        """记录 API 调用"""
        self._calls.append({
            "timestamp": datetime.now(),
            "path": path,
            "method": method,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "user_id": user_id
        })
        if len(self._calls) > self._max_records:
            self._calls = self._calls[-self._max_records:]
    
    def get_stats(self, hours: int = 24) -> Dict[str, Any]:
        """获取 API 统计"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [c for c in self._calls if c["timestamp"] >= cutoff]
        
        if not recent:
            return {"total_calls": 0, "avg_response_time": 0, "error_rate": 0}
        
        total = len(recent)
        avg_time = sum(c["response_time_ms"] for c in recent) / total
        errors = sum(1 for c in recent if c["status_code"] >= 400)
        
        by_endpoint = defaultdict(lambda: {"count": 0, "total_time": 0})
        for c in recent:
            ep = by_endpoint[c["path"]]
            ep["count"] += 1
            ep["total_time"] += c["response_time_ms"]
        
        top_endpoints = sorted(
            [{"path": k, "count": v["count"], "avg_time": v["total_time"] / v["count"]}
             for k, v in by_endpoint.items()],
            key=lambda x: x["count"], reverse=True
        )[:10]
        
        by_status = defaultdict(int)
        for c in recent:
            by_status[str(c["status_code"])] += 1
        
        return {
            "time_range_hours": hours,
            "total_calls": total,
            "avg_response_time_ms": round(avg_time, 2),
            "error_rate": round(errors / total * 100, 2),
            "error_count": errors,
            "top_endpoints": top_endpoints,
            "by_status": dict(by_status)
        }
    
    def get_timeline(self, hours: int = 24, interval_minutes: int = 60) -> List[Dict]:
        """获取时间线数据"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [c for c in self._calls if c["timestamp"] >= cutoff]
        
        timeline = []
        current = cutoff
        interval = timedelta(minutes=interval_minutes)
        
        while current < datetime.now():
            next_time = current + interval
            period = [c for c in recent if current <= c["timestamp"] < next_time]
            
            timeline.append({
                "time": current.strftime("%H:%M"),
                "count": len(period),
                "avg_time": round(sum(c["response_time_ms"] for c in period) / len(period), 2) if period else 0,
                "errors": sum(1 for c in period if c["status_code"] >= 400)
            })
            current = next_time
        
        return timeline


api_stats_service = APIStatsService()


def get_api_stats_service() -> APIStatsService:
    return api_stats_service
