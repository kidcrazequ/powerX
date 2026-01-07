"""
PowerX 定时报表服务
创建日期: 2026-01-07
作者: zhi.qu
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.report_schedule import ReportSchedule, ScheduledReportLog, ScheduleFrequency
from app.services.queue_service import get_queue_service


class ScheduledReportService:
    """定时报表服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_schedule(
        self,
        name: str,
        template_id: int,
        frequency: str,
        schedule_time: time,
        recipients: List[str],
        parameters: Dict[str, Any] = None,
        schedule_day: int = None,
        send_email: bool = True,
        send_wechat: bool = False,
        created_by: str = None
    ) -> ReportSchedule:
        """创建调度配置"""
        schedule_id = f"SCH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        schedule = ReportSchedule(
            schedule_id=schedule_id,
            name=name,
            template_id=template_id,
            frequency=frequency,
            schedule_time=schedule_time,
            schedule_day=schedule_day,
            recipients=recipients,
            parameters=parameters,
            send_email=send_email,
            send_wechat=send_wechat,
            is_active=True,
            created_by=created_by
        )
        
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        
        logger.info(f"创建报表调度: {schedule_id}")
        return schedule
    
    async def get_schedule(self, schedule_id: str) -> Optional[ReportSchedule]:
        """获取调度配置"""
        query = select(ReportSchedule).where(ReportSchedule.schedule_id == schedule_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def list_schedules(self, is_active: bool = None) -> List[ReportSchedule]:
        """列出调度配置"""
        query = select(ReportSchedule)
        if is_active is not None:
            query = query.where(ReportSchedule.is_active == is_active)
        query = query.order_by(ReportSchedule.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_schedule(
        self,
        schedule_id: str,
        **updates
    ) -> Optional[ReportSchedule]:
        """更新调度配置"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        for key, value in updates.items():
            if hasattr(schedule, key) and value is not None:
                setattr(schedule, key, value)
        
        await self.db.commit()
        await self.db.refresh(schedule)
        
        logger.info(f"更新报表调度: {schedule_id}")
        return schedule
    
    async def toggle_schedule(self, schedule_id: str, is_active: bool) -> bool:
        """启用/禁用调度"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False
        
        schedule.is_active = is_active
        await self.db.commit()
        
        logger.info(f"{'启用' if is_active else '禁用'}报表调度: {schedule_id}")
        return True
    
    async def delete_schedule(self, schedule_id: str) -> bool:
        """删除调度配置"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False
        
        await self.db.delete(schedule)
        await self.db.commit()
        
        logger.info(f"删除报表调度: {schedule_id}")
        return True
    
    async def get_due_schedules(self) -> List[ReportSchedule]:
        """获取待执行的调度"""
        now = datetime.now()
        current_time = now.time()
        current_weekday = now.weekday() + 1  # 1-7
        current_day = now.day
        
        query = select(ReportSchedule).where(ReportSchedule.is_active == True)
        result = await self.db.execute(query)
        schedules = result.scalars().all()
        
        due_schedules = []
        for schedule in schedules:
            is_due = False
            
            if schedule.frequency == ScheduleFrequency.DAILY.value:
                # 每天执行
                is_due = True
            elif schedule.frequency == ScheduleFrequency.WEEKLY.value:
                # 每周执行
                is_due = (schedule.schedule_day == current_weekday)
            elif schedule.frequency == ScheduleFrequency.MONTHLY.value:
                # 每月执行
                is_due = (schedule.schedule_day == current_day)
            
            # 检查时间
            if is_due and schedule.schedule_time:
                schedule_hour = schedule.schedule_time.hour
                schedule_minute = schedule.schedule_time.minute
                
                # 检查是否在执行时间窗口内 (±5分钟)
                schedule_minutes = schedule_hour * 60 + schedule_minute
                current_minutes = current_time.hour * 60 + current_time.minute
                
                if abs(schedule_minutes - current_minutes) <= 5:
                    # 检查今天是否已执行
                    if schedule.last_run_at:
                        last_run_date = schedule.last_run_at.date()
                        if last_run_date == now.date():
                            continue
                    
                    due_schedules.append(schedule)
        
        return due_schedules
    
    async def execute_schedule(self, schedule_id: str) -> ScheduledReportLog:
        """执行调度"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            raise ValueError(f"调度不存在: {schedule_id}")
        
        run_id = f"RUN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        log = ScheduledReportLog(
            schedule_id=schedule_id,
            run_id=run_id,
            started_at=datetime.now(),
            recipients_count=len(schedule.recipients) if schedule.recipients else 0
        )
        
        try:
            # 发送到队列执行报表生成
            queue_service = get_queue_service()
            await queue_service.publish_report_generation(
                report_id=run_id,
                template_id=schedule.template_id,
                parameters=schedule.parameters or {},
                user_id=schedule.created_by or "system"
            )
            
            log.status = "success"
            log.completed_at = datetime.now()
            log.sent_count = log.recipients_count
            
            # 更新调度状态
            schedule.last_run_at = datetime.now()
            schedule.last_run_status = "success"
            schedule.run_count = (schedule.run_count or 0) + 1
            
            logger.info(f"执行报表调度成功: {schedule_id}")
            
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.now()
            
            schedule.last_run_at = datetime.now()
            schedule.last_run_status = "failed"
            
            logger.error(f"执行报表调度失败: {schedule_id}, {e}")
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        return log
    
    async def get_schedule_logs(
        self,
        schedule_id: str,
        limit: int = 20
    ) -> List[ScheduledReportLog]:
        """获取调度执行日志"""
        query = select(ScheduledReportLog).where(
            ScheduledReportLog.schedule_id == schedule_id
        ).order_by(ScheduledReportLog.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


def get_scheduled_report_service(db: AsyncSession) -> ScheduledReportService:
    """获取定时报表服务"""
    return ScheduledReportService(db)
