"""
PowerX 交易日历服务
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from app.models.trading_calendar import TradingCalendar, TradingSession, Holiday


# 默认交易时段
DEFAULT_SESSIONS = {
    "spot": [
        {"name": "日前集中竞价", "start": time(9, 0), "end": time(10, 30)},
        {"name": "日前挂牌", "start": time(10, 30), "end": time(11, 30)},
        {"name": "日前双边协商", "start": time(14, 0), "end": time(15, 0)},
        {"name": "实时调整", "start": time(15, 30), "end": time(16, 30)}
    ],
    "mid_long": [
        {"name": "月度集中竞价", "start": time(9, 0), "end": time(12, 0)},
        {"name": "双边协商", "start": time(14, 0), "end": time(17, 0)}
    ]
}

# 中国法定节假日 (2026年示例)
HOLIDAYS_2026 = [
    {"name": "元旦", "start": "2026-01-01", "end": "2026-01-03"},
    {"name": "春节", "start": "2026-02-17", "end": "2026-02-23"},
    {"name": "清明节", "start": "2026-04-04", "end": "2026-04-06"},
    {"name": "劳动节", "start": "2026-05-01", "end": "2026-05-05"},
    {"name": "端午节", "start": "2026-05-31", "end": "2026-06-02"},
    {"name": "中秋节", "start": "2026-09-27", "end": "2026-09-29"},
    {"name": "国庆节", "start": "2026-10-01", "end": "2026-10-07"}
]


class CalendarService:
    """交易日历服务"""
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
        self._holidays_cache: Dict[int, List[date]] = {}
    
    async def is_trading_day(self, check_date: date, province: str = "guangdong") -> bool:
        """检查是否为交易日"""
        # 周末不交易
        if check_date.weekday() >= 5:
            return False
        
        # 检查是否节假日
        if await self.is_holiday(check_date, province):
            return False
        
        return True
    
    async def is_holiday(self, check_date: date, province: str = None) -> bool:
        """检查是否为节假日"""
        # 从缓存或数据库获取节假日
        year = check_date.year
        
        if year not in self._holidays_cache:
            self._holidays_cache[year] = await self._load_holidays(year, province)
        
        return check_date in self._holidays_cache[year]
    
    async def _load_holidays(self, year: int, province: str = None) -> List[date]:
        """加载节假日列表"""
        holidays = []
        
        if self.db:
            query = select(Holiday).where(
                Holiday.start_date >= date(year, 1, 1),
                Holiday.end_date <= date(year, 12, 31)
            )
            result = await self.db.execute(query)
            holiday_records = result.scalars().all()
            
            for h in holiday_records:
                current = h.start_date
                while current <= h.end_date:
                    holidays.append(current)
                    current += timedelta(days=1)
        else:
            # 使用默认节假日
            for h in HOLIDAYS_2026:
                start = datetime.strptime(h["start"], "%Y-%m-%d").date()
                end = datetime.strptime(h["end"], "%Y-%m-%d").date()
                current = start
                while current <= end:
                    holidays.append(current)
                    current += timedelta(days=1)
        
        return holidays
    
    async def get_next_trading_day(self, from_date: date, province: str = "guangdong") -> date:
        """获取下一个交易日"""
        next_date = from_date + timedelta(days=1)
        max_attempts = 30
        
        for _ in range(max_attempts):
            if await self.is_trading_day(next_date, province):
                return next_date
            next_date += timedelta(days=1)
        
        return next_date
    
    async def get_trading_days_in_range(
        self, 
        start_date: date, 
        end_date: date, 
        province: str = "guangdong"
    ) -> List[date]:
        """获取日期范围内的所有交易日"""
        trading_days = []
        current = start_date
        
        while current <= end_date:
            if await self.is_trading_day(current, province):
                trading_days.append(current)
            current += timedelta(days=1)
        
        return trading_days
    
    def get_trading_sessions(self, market_type: str = "spot") -> List[Dict[str, Any]]:
        """获取交易时段"""
        sessions = DEFAULT_SESSIONS.get(market_type, [])
        return [
            {
                "name": s["name"],
                "start_time": s["start"].strftime("%H:%M"),
                "end_time": s["end"].strftime("%H:%M")
            }
            for s in sessions
        ]
    
    def is_in_trading_session(
        self, 
        check_time: datetime = None, 
        market_type: str = "spot"
    ) -> Dict[str, Any]:
        """检查是否在交易时段内"""
        if check_time is None:
            check_time = datetime.now()
        
        current_time = check_time.time()
        sessions = DEFAULT_SESSIONS.get(market_type, [])
        
        for session in sessions:
            if session["start"] <= current_time <= session["end"]:
                return {
                    "is_open": True,
                    "session_name": session["name"],
                    "ends_at": session["end"].strftime("%H:%M")
                }
        
        # 找下一个时段
        for session in sessions:
            if current_time < session["start"]:
                return {
                    "is_open": False,
                    "next_session": session["name"],
                    "opens_at": session["start"].strftime("%H:%M")
                }
        
        return {
            "is_open": False,
            "next_session": sessions[0]["name"] if sessions else None,
            "opens_at": sessions[0]["start"].strftime("%H:%M") if sessions else None,
            "note": "今日交易时段已结束"
        }
    
    async def get_calendar_month(
        self, 
        year: int, 
        month: int, 
        province: str = "guangdong"
    ) -> List[Dict[str, Any]]:
        """获取月度日历"""
        from calendar import monthrange
        
        _, days_in_month = monthrange(year, month)
        calendar_data = []
        
        for day in range(1, days_in_month + 1):
            current_date = date(year, month, day)
            is_trading = await self.is_trading_day(current_date, province)
            is_holiday = await self.is_holiday(current_date, province)
            
            calendar_data.append({
                "date": current_date.isoformat(),
                "day": day,
                "weekday": current_date.weekday(),
                "is_trading_day": is_trading,
                "is_weekend": current_date.weekday() >= 5,
                "is_holiday": is_holiday
            })
        
        return calendar_data
    
    async def add_holiday(
        self,
        name: str,
        start_date: date,
        end_date: date,
        holiday_type: str = "national"
    ) -> Holiday:
        """添加节假日"""
        holiday = Holiday(
            name=name,
            start_date=start_date,
            end_date=end_date,
            holiday_type=holiday_type
        )
        
        self.db.add(holiday)
        await self.db.commit()
        
        # 清除缓存
        year = start_date.year
        if year in self._holidays_cache:
            del self._holidays_cache[year]
        
        logger.info(f"添加节假日: {name} ({start_date} - {end_date})")
        return holiday


# 单例
calendar_service = CalendarService()


def get_calendar_service(db: AsyncSession = None) -> CalendarService:
    """获取日历服务"""
    if db:
        calendar_service.db = db
    return calendar_service
