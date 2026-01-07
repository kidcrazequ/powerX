"""
PowerX 预测对账服务
创建日期: 2026-01-07
作者: zhi.qu

预测结果与实际结果对比分析
"""
import uuid
import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from loguru import logger

from app.models.prediction_record import PredictionRecord, ReconciliationReport


class PredictionReconciliationService:
    """预测对账服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_prediction(
        self,
        prediction_type: str,
        province: str,
        target_time: datetime,
        predicted_value: float,
        confidence: float = 0.8,
        range_low: float = None,
        range_high: float = None,
        model_name: str = "deepseek_v3",
        market_type: str = "spot",
        input_features: Dict[str, Any] = None
    ) -> PredictionRecord:
        """创建预测记录"""
        prediction_id = f"PRED-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # 如果没有指定区间，默认±5%
        if range_low is None:
            range_low = predicted_value * 0.95
        if range_high is None:
            range_high = predicted_value * 1.05
        
        record = PredictionRecord(
            prediction_id=prediction_id,
            prediction_type=prediction_type,
            province=province,
            market_type=market_type,
            target_time=target_time,
            predicted_value=predicted_value,
            predicted_range_low=range_low,
            predicted_range_high=range_high,
            confidence=confidence,
            model_name=model_name,
            input_features=input_features
        )
        
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        
        logger.debug(f"创建预测记录: {prediction_id}")
        return record
    
    async def reconcile_prediction(
        self,
        prediction_id: str,
        actual_value: float
    ) -> PredictionRecord:
        """对账单个预测"""
        query = select(PredictionRecord).where(
            PredictionRecord.prediction_id == prediction_id
        )
        result = await self.db.execute(query)
        record = result.scalars().first()
        
        if not record:
            raise ValueError(f"预测记录不存在: {prediction_id}")
        
        if record.is_reconciled:
            logger.warning(f"预测已对账: {prediction_id}")
            return record
        
        record.actual_value = actual_value
        record.is_reconciled = True
        record.reconciled_at = datetime.now()
        
        # 计算误差
        record.error = actual_value - record.predicted_value
        if record.predicted_value != 0:
            record.error_percentage = abs(record.error / record.predicted_value * 100)
        
        # 检查是否在预测区间内
        record.within_range = (
            record.predicted_range_low <= actual_value <= record.predicted_range_high
        )
        
        await self.db.commit()
        
        logger.info(f"预测对账完成: {prediction_id}, 误差: {record.error_percentage:.2f}%")
        return record
    
    async def batch_reconcile(
        self,
        prediction_type: str = None,
        province: str = None,
        before_time: datetime = None
    ) -> int:
        """批量对账"""
        # 获取待对账的预测
        query = select(PredictionRecord).where(
            PredictionRecord.is_reconciled == False,
            PredictionRecord.target_time <= datetime.now()
        )
        
        if prediction_type:
            query = query.where(PredictionRecord.prediction_type == prediction_type)
        if province:
            query = query.where(PredictionRecord.province == province)
        if before_time:
            query = query.where(PredictionRecord.target_time <= before_time)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        reconciled_count = 0
        for record in records:
            # 这里应该从实际数据源获取真实值
            # 目前使用模拟数据
            import random
            actual_value = record.predicted_value * (1 + random.uniform(-0.1, 0.1))
            
            await self.reconcile_prediction(record.prediction_id, actual_value)
            reconciled_count += 1
        
        logger.info(f"批量对账完成: {reconciled_count} 条记录")
        return reconciled_count
    
    async def generate_report(
        self,
        period_type: str = "daily",
        prediction_type: str = None,
        province: str = None
    ) -> ReconciliationReport:
        """生成对账报告"""
        now = datetime.now()
        
        if period_type == "daily":
            period_start = now - timedelta(days=1)
        elif period_type == "weekly":
            period_start = now - timedelta(weeks=1)
        else:
            period_start = now - timedelta(days=30)
        
        # 获取已对账的预测
        query = select(PredictionRecord).where(
            and_(
                PredictionRecord.is_reconciled == True,
                PredictionRecord.reconciled_at >= period_start,
                PredictionRecord.reconciled_at <= now
            )
        )
        
        if prediction_type:
            query = query.where(PredictionRecord.prediction_type == prediction_type)
        if province:
            query = query.where(PredictionRecord.province == province)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        if not records:
            return None
        
        # 计算统计指标
        total = len(records)
        errors = [r.error for r in records if r.error is not None]
        error_pcts = [r.error_percentage for r in records if r.error_percentage is not None]
        within_range_count = sum(1 for r in records if r.within_range)
        
        mae = sum(abs(e) for e in errors) / len(errors) if errors else 0
        mape = sum(error_pcts) / len(error_pcts) if error_pcts else 0
        mse = sum(e ** 2 for e in errors) / len(errors) if errors else 0
        rmse = math.sqrt(mse)
        
        range_hit_rate = within_range_count / total if total > 0 else 0
        
        # 计算趋势准确率
        trend_correct = 0
        for i, r in enumerate(records[1:], 1):
            prev = records[i - 1]
            if prev.predicted_value and r.predicted_value and prev.actual_value and r.actual_value:
                pred_trend = r.predicted_value - prev.predicted_value
                actual_trend = r.actual_value - prev.actual_value
                if (pred_trend >= 0 and actual_trend >= 0) or (pred_trend < 0 and actual_trend < 0):
                    trend_correct += 1
        
        trend_accuracy = trend_correct / (total - 1) if total > 1 else 0
        
        # 创建报告
        report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        report = ReconciliationReport(
            report_id=report_id,
            period_type=period_type,
            period_start=period_start,
            period_end=now,
            prediction_type=prediction_type,
            province=province,
            total_predictions=total,
            reconciled_count=total,
            accuracy=1 - mape / 100 if mape else 1,
            mae=round(mae, 2),
            mape=round(mape, 2),
            rmse=round(rmse, 2),
            range_hit_rate=round(range_hit_rate, 4),
            trend_accuracy=round(trend_accuracy, 4),
            details={
                "error_distribution": {
                    "min": min(error_pcts) if error_pcts else 0,
                    "max": max(error_pcts) if error_pcts else 0,
                    "median": sorted(error_pcts)[len(error_pcts)//2] if error_pcts else 0
                }
            }
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        logger.info(f"生成对账报告: {report_id}, MAPE: {mape:.2f}%")
        return report
    
    async def get_accuracy_trend(
        self,
        prediction_type: str = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """获取准确率趋势"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = select(PredictionRecord).where(
            and_(
                PredictionRecord.is_reconciled == True,
                PredictionRecord.reconciled_at >= start_date
            )
        )
        
        if prediction_type:
            query = query.where(PredictionRecord.prediction_type == prediction_type)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        # 按日期分组
        daily_data = {}
        for r in records:
            date_key = r.reconciled_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = []
            daily_data[date_key].append(r)
        
        trend = []
        for date_key in sorted(daily_data.keys()):
            day_records = daily_data[date_key]
            error_pcts = [r.error_percentage for r in day_records if r.error_percentage is not None]
            within_range = sum(1 for r in day_records if r.within_range)
            
            trend.append({
                "date": date_key,
                "count": len(day_records),
                "mape": round(sum(error_pcts) / len(error_pcts), 2) if error_pcts else 0,
                "range_hit_rate": round(within_range / len(day_records), 4) if day_records else 0
            })
        
        return trend
    
    async def get_prediction_summary(
        self,
        prediction_id: str
    ) -> Dict[str, Any]:
        """获取预测摘要"""
        query = select(PredictionRecord).where(
            PredictionRecord.prediction_id == prediction_id
        )
        result = await self.db.execute(query)
        record = result.scalars().first()
        
        if not record:
            return None
        
        return {
            "prediction_id": record.prediction_id,
            "prediction_type": record.prediction_type,
            "province": record.province,
            "target_time": record.target_time.isoformat() if record.target_time else None,
            "predicted_value": record.predicted_value,
            "predicted_range": [record.predicted_range_low, record.predicted_range_high],
            "confidence": record.confidence,
            "actual_value": record.actual_value,
            "is_reconciled": record.is_reconciled,
            "error_percentage": record.error_percentage,
            "within_range": record.within_range
        }


def get_prediction_reconciliation_service(db: AsyncSession) -> PredictionReconciliationService:
    """获取预测对账服务"""
    return PredictionReconciliationService(db)
