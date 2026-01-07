"""
PowerX 自动学习服务
创建日期: 2026-01-07
作者: zhi.qu

根据历史交易结果自动优化策略
"""
import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from loguru import logger

from app.models.learning_record import LearningRecord, StrategyOptimization, ModelPerformance


class AutoLearningService:
    """自动学习服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_prediction(
        self,
        model_name: str,
        strategy_id: str,
        input_data: Dict[str, Any],
        predicted_value: float,
        predicted_direction: str
    ) -> LearningRecord:
        """记录预测"""
        record = LearningRecord(
            model_name=model_name,
            strategy_id=strategy_id,
            learning_type="prediction",
            input_data=input_data,
            predicted_value=predicted_value,
            predicted_direction=predicted_direction,
            prediction_time=datetime.now()
        )
        
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        
        return record
    
    async def record_actual_result(
        self,
        record_id: int,
        actual_value: float
    ) -> LearningRecord:
        """记录实际结果"""
        query = select(LearningRecord).where(LearningRecord.id == record_id)
        result = await self.db.execute(query)
        record = result.scalars().first()
        
        if not record:
            raise ValueError(f"记录不存在: {record_id}")
        
        # 计算误差
        record.actual_value = actual_value
        record.actual_time = datetime.now()
        
        if record.predicted_value:
            record.error = actual_value - record.predicted_value
            if record.predicted_value != 0:
                record.error_percentage = abs(record.error / record.predicted_value * 100)
        
        # 判断方向
        if record.predicted_value:
            if actual_value > record.predicted_value:
                record.actual_direction = "up"
            elif actual_value < record.predicted_value:
                record.actual_direction = "down"
            else:
                record.actual_direction = "stable"
            
            record.direction_correct = (record.actual_direction == record.predicted_direction)
        
        await self.db.commit()
        
        logger.debug(f"记录实际结果: {record_id}, 误差: {record.error_percentage:.2f}%")
        return record
    
    async def record_feedback(
        self,
        record_id: int,
        score: float,
        comment: str = None
    ):
        """记录用户反馈"""
        query = select(LearningRecord).where(LearningRecord.id == record_id)
        result = await self.db.execute(query)
        record = result.scalars().first()
        
        if record:
            record.feedback_score = score
            record.feedback_comment = comment
            await self.db.commit()
    
    async def calculate_model_performance(
        self,
        model_name: str,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """计算模型性能"""
        now = datetime.now()
        
        if period == "daily":
            period_start = now - timedelta(days=1)
        elif period == "weekly":
            period_start = now - timedelta(weeks=1)
        else:
            period_start = now - timedelta(days=30)
        
        query = select(LearningRecord).where(
            and_(
                LearningRecord.model_name == model_name,
                LearningRecord.actual_value.isnot(None),
                LearningRecord.created_at >= period_start
            )
        )
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        if not records:
            return {"message": "无数据"}
        
        # 计算指标
        errors = [r.error for r in records if r.error is not None]
        error_pcts = [r.error_percentage for r in records if r.error_percentage is not None]
        directions = [r.direction_correct for r in records if r.direction_correct is not None]
        
        total = len(records)
        correct = sum(1 for d in directions if d)
        
        mae = sum(abs(e) for e in errors) / len(errors) if errors else 0
        mse = sum(e ** 2 for e in errors) / len(errors) if errors else 0
        rmse = math.sqrt(mse)
        mape = sum(error_pcts) / len(error_pcts) if error_pcts else 0
        
        direction_accuracy = correct / len(directions) if directions else 0
        
        # 保存性能记录
        performance = ModelPerformance(
            model_name=model_name,
            period=period,
            period_start=period_start,
            period_end=now,
            total_predictions=total,
            correct_predictions=correct,
            accuracy=correct / total if total > 0 else 0,
            mae=mae,
            mse=mse,
            rmse=rmse,
            mape=mape,
            direction_accuracy=direction_accuracy
        )
        
        self.db.add(performance)
        await self.db.commit()
        
        return {
            "model_name": model_name,
            "period": period,
            "total_predictions": total,
            "accuracy": round(direction_accuracy, 4),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "direction_accuracy": round(direction_accuracy, 4)
        }
    
    async def optimize_strategy(
        self,
        strategy_id: str,
        current_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """优化策略参数"""
        # 获取该策略的历史记录
        query = select(LearningRecord).where(
            and_(
                LearningRecord.strategy_id == strategy_id,
                LearningRecord.actual_value.isnot(None)
            )
        ).order_by(LearningRecord.created_at.desc()).limit(100)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        if len(records) < 20:
            return {
                "optimized": False,
                "reason": "数据不足，需要至少20条历史记录"
            }
        
        # 分析误差模式
        errors = [r.error for r in records if r.error is not None]
        avg_error = sum(errors) / len(errors) if errors else 0
        
        # 计算优化建议
        optimized_params = current_params.copy()
        suggestions = []
        
        # 如果平均误差偏高，调整预测窗口
        if abs(avg_error) > 5:
            if "prediction_window" in optimized_params:
                old_window = optimized_params["prediction_window"]
                new_window = old_window * 0.9 if avg_error > 0 else old_window * 1.1
                optimized_params["prediction_window"] = round(new_window, 2)
                suggestions.append(f"调整预测窗口: {old_window} -> {new_window:.2f}")
        
        # 如果方向准确率低，调整信心阈值
        direction_correct = [r.direction_correct for r in records if r.direction_correct is not None]
        direction_accuracy = sum(1 for d in direction_correct if d) / len(direction_correct) if direction_correct else 0
        
        if direction_accuracy < 0.6:
            if "confidence_threshold" in optimized_params:
                old_threshold = optimized_params["confidence_threshold"]
                new_threshold = min(0.9, old_threshold + 0.1)
                optimized_params["confidence_threshold"] = new_threshold
                suggestions.append(f"提高信心阈值: {old_threshold} -> {new_threshold}")
        
        # 保存优化记录
        optimization = StrategyOptimization(
            strategy_id=strategy_id,
            params_before=current_params,
            params_after=optimized_params,
            optimization_reason="; ".join(suggestions) if suggestions else "无需优化",
            performance_before={
                "avg_error": avg_error,
                "direction_accuracy": direction_accuracy
            }
        )
        
        self.db.add(optimization)
        await self.db.commit()
        
        logger.info(f"策略优化: {strategy_id}, 建议: {suggestions}")
        
        return {
            "optimized": len(suggestions) > 0,
            "strategy_id": strategy_id,
            "original_params": current_params,
            "optimized_params": optimized_params,
            "suggestions": suggestions,
            "metrics": {
                "avg_error": round(avg_error, 2),
                "direction_accuracy": round(direction_accuracy, 4)
            }
        }
    
    async def get_learning_history(
        self,
        model_name: str = None,
        strategy_id: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取学习历史"""
        query = select(LearningRecord)
        
        if model_name:
            query = query.where(LearningRecord.model_name == model_name)
        if strategy_id:
            query = query.where(LearningRecord.strategy_id == strategy_id)
        
        query = query.order_by(LearningRecord.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return [
            {
                "id": r.id,
                "model_name": r.model_name,
                "strategy_id": r.strategy_id,
                "predicted_value": r.predicted_value,
                "actual_value": r.actual_value,
                "error_percentage": r.error_percentage,
                "direction_correct": r.direction_correct,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]


def get_auto_learning_service(db: AsyncSession) -> AutoLearningService:
    """获取自动学习服务"""
    return AutoLearningService(db)
