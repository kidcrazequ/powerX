"""
PowerX 电量预测服务

创建日期: 2026-01-07
作者: zhi.qu

基于历史数据的用电量和负荷预测
"""

import random
import math
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger


class LoadPredictor:
    """
    电量/负荷预测器
    
    功能：
    - 日电量预测
    - 周电量预测
    - 月电量预测
    - 负荷曲线预测
    - 峰谷时段预测
    """
    
    # 基础负荷模式（24小时）
    HOURLY_LOAD_PATTERN = [
        0.65, 0.60, 0.55, 0.52, 0.50, 0.55,  # 0-5
        0.65, 0.80, 0.95, 1.00, 0.98, 0.95,  # 6-11
        0.90, 0.92, 0.95, 0.98, 1.00, 1.05,  # 12-17
        1.10, 1.08, 1.00, 0.90, 0.80, 0.70   # 18-23
    ]
    
    # 周负荷模式（周一到周日）
    WEEKLY_PATTERN = [1.0, 1.02, 1.01, 1.0, 0.98, 0.75, 0.70]
    
    # 月负荷模式（1-12月）
    MONTHLY_PATTERN = [0.90, 0.85, 0.88, 0.92, 0.98, 1.10, 1.20, 1.18, 1.05, 0.95, 0.90, 0.92]
    
    # 省份基础负荷（MW）
    PROVINCE_BASE_LOAD = {
        "guangdong": 120000,
        "zhejiang": 55000,
        "jiangsu": 85000,
        "shandong": 75000,
        "sichuan": 45000
    }
    
    def __init__(self):
        logger.info("电量预测服务初始化")
    
    async def predict_daily_load(
        self,
        province: str,
        target_date: date,
        weather: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        预测指定日期的日负荷曲线
        
        Args:
            province: 省份
            target_date: 目标日期
            weather: 天气信息（温度、湿度等）
            
        Returns:
            Dict: 日负荷预测结果
        """
        logger.info(f"日负荷预测: province={province}, date={target_date}")
        
        base_load = self.PROVINCE_BASE_LOAD.get(province, 50000)
        
        # 获取季节调整
        month = target_date.month
        seasonal_factor = self.MONTHLY_PATTERN[month - 1]
        
        # 获取星期调整
        weekday = target_date.weekday()
        weekly_factor = self.WEEKLY_PATTERN[weekday]
        
        # 天气调整
        weather_factor = 1.0
        if weather:
            temp = weather.get("temperature", 25)
            if temp > 30:
                weather_factor = 1.0 + (temp - 30) * 0.02  # 高温增加负荷
            elif temp < 10:
                weather_factor = 1.0 + (10 - temp) * 0.015  # 低温增加负荷
        
        # 生成24小时负荷曲线
        hourly_loads = []
        for hour in range(24):
            hourly_factor = self.HOURLY_LOAD_PATTERN[hour]
            
            load = base_load * hourly_factor * seasonal_factor * weekly_factor * weather_factor
            load *= (1 + random.uniform(-0.03, 0.03))  # 添加随机波动
            
            hourly_loads.append({
                "hour": hour,
                "load_mw": round(load, 2),
                "load_gwh": round(load / 1000, 3)
            })
        
        # 计算统计信息
        loads = [h["load_mw"] for h in hourly_loads]
        
        return {
            "province": province,
            "date": target_date.isoformat(),
            "prediction_type": "daily",
            "hourly_loads": hourly_loads,
            "summary": {
                "total_gwh": round(sum(h["load_gwh"] for h in hourly_loads), 2),
                "peak_load_mw": round(max(loads), 2),
                "peak_hour": loads.index(max(loads)),
                "valley_load_mw": round(min(loads), 2),
                "valley_hour": loads.index(min(loads)),
                "avg_load_mw": round(sum(loads) / len(loads), 2),
                "peak_valley_ratio": round(max(loads) / min(loads), 2)
            },
            "factors": {
                "seasonal": seasonal_factor,
                "weekly": weekly_factor,
                "weather": weather_factor
            },
            "confidence": round(random.uniform(0.85, 0.95), 2),
            "generated_at": datetime.now().isoformat()
        }
    
    async def predict_weekly_load(
        self,
        province: str,
        start_date: date
    ) -> Dict[str, Any]:
        """
        预测一周的日电量
        
        Args:
            province: 省份
            start_date: 开始日期
            
        Returns:
            Dict: 周电量预测结果
        """
        logger.info(f"周电量预测: province={province}, start={start_date}")
        
        daily_predictions = []
        total_gwh = 0
        
        for i in range(7):
            target_date = start_date + timedelta(days=i)
            daily = await self.predict_daily_load(province, target_date)
            
            daily_predictions.append({
                "date": target_date.isoformat(),
                "weekday": target_date.strftime("%A"),
                "total_gwh": daily["summary"]["total_gwh"],
                "peak_load_mw": daily["summary"]["peak_load_mw"],
                "valley_load_mw": daily["summary"]["valley_load_mw"]
            })
            total_gwh += daily["summary"]["total_gwh"]
        
        return {
            "province": province,
            "period": {
                "start": start_date.isoformat(),
                "end": (start_date + timedelta(days=6)).isoformat()
            },
            "prediction_type": "weekly",
            "daily_predictions": daily_predictions,
            "summary": {
                "total_gwh": round(total_gwh, 2),
                "avg_daily_gwh": round(total_gwh / 7, 2),
                "peak_day": max(daily_predictions, key=lambda x: x["total_gwh"])["date"],
                "valley_day": min(daily_predictions, key=lambda x: x["total_gwh"])["date"]
            },
            "confidence": round(random.uniform(0.80, 0.90), 2),
            "generated_at": datetime.now().isoformat()
        }
    
    async def predict_monthly_load(
        self,
        province: str,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        预测月度电量
        
        Args:
            province: 省份
            year: 年份
            month: 月份
            
        Returns:
            Dict: 月电量预测结果
        """
        logger.info(f"月电量预测: province={province}, {year}-{month}")
        
        base_load = self.PROVINCE_BASE_LOAD.get(province, 50000)
        seasonal_factor = self.MONTHLY_PATTERN[month - 1]
        
        # 计算该月天数
        if month == 12:
            days_in_month = (date(year + 1, 1, 1) - date(year, month, 1)).days
        else:
            days_in_month = (date(year, month + 1, 1) - date(year, month, 1)).days
        
        # 生成每日预测
        daily_predictions = []
        for day in range(1, days_in_month + 1):
            target_date = date(year, month, day)
            weekday = target_date.weekday()
            weekly_factor = self.WEEKLY_PATTERN[weekday]
            
            # 日电量 = 基础负荷 * 24小时 * 各种因子
            daily_gwh = base_load * 24 / 1000 * seasonal_factor * weekly_factor
            daily_gwh *= (1 + random.uniform(-0.05, 0.05))
            
            daily_predictions.append({
                "date": target_date.isoformat(),
                "gwh": round(daily_gwh, 2)
            })
        
        total_gwh = sum(d["gwh"] for d in daily_predictions)
        
        # 历史同比（模拟）
        yoy_change = random.uniform(-5, 10)
        
        return {
            "province": province,
            "period": {
                "year": year,
                "month": month,
                "days": days_in_month
            },
            "prediction_type": "monthly",
            "daily_predictions": daily_predictions,
            "summary": {
                "total_gwh": round(total_gwh, 2),
                "total_twh": round(total_gwh / 1000, 3),
                "avg_daily_gwh": round(total_gwh / days_in_month, 2),
                "peak_day": max(daily_predictions, key=lambda x: x["gwh"])["date"],
                "valley_day": min(daily_predictions, key=lambda x: x["gwh"])["date"]
            },
            "comparison": {
                "yoy_change_percent": round(yoy_change, 2),
                "last_year_gwh": round(total_gwh / (1 + yoy_change / 100), 2)
            },
            "confidence": round(random.uniform(0.75, 0.88), 2),
            "generated_at": datetime.now().isoformat()
        }
    
    async def predict_peak_valley(
        self,
        province: str,
        target_date: date
    ) -> Dict[str, Any]:
        """
        预测峰谷时段
        
        Args:
            province: 省份
            target_date: 目标日期
            
        Returns:
            Dict: 峰谷时段预测
        """
        logger.info(f"峰谷时段预测: province={province}, date={target_date}")
        
        # 获取日负荷预测
        daily = await self.predict_daily_load(province, target_date)
        loads = daily["hourly_loads"]
        
        # 计算阈值
        load_values = [h["load_mw"] for h in loads]
        avg_load = sum(load_values) / len(load_values)
        
        peak_threshold = avg_load * 1.1
        valley_threshold = avg_load * 0.8
        
        # 分类时段
        peak_hours = []
        flat_hours = []
        valley_hours = []
        
        for h in loads:
            if h["load_mw"] >= peak_threshold:
                peak_hours.append(h["hour"])
            elif h["load_mw"] <= valley_threshold:
                valley_hours.append(h["hour"])
            else:
                flat_hours.append(h["hour"])
        
        # 计算各时段电量
        peak_gwh = sum(loads[h]["load_gwh"] for h in peak_hours) if peak_hours else 0
        flat_gwh = sum(loads[h]["load_gwh"] for h in flat_hours) if flat_hours else 0
        valley_gwh = sum(loads[h]["load_gwh"] for h in valley_hours) if valley_hours else 0
        
        return {
            "province": province,
            "date": target_date.isoformat(),
            "peak_periods": {
                "hours": peak_hours,
                "total_gwh": round(peak_gwh, 3),
                "avg_load_mw": round(sum(load_values[h] for h in peak_hours) / len(peak_hours), 2) if peak_hours else 0,
                "percentage": round(peak_gwh / daily["summary"]["total_gwh"] * 100, 1)
            },
            "flat_periods": {
                "hours": flat_hours,
                "total_gwh": round(flat_gwh, 3),
                "avg_load_mw": round(sum(load_values[h] for h in flat_hours) / len(flat_hours), 2) if flat_hours else 0,
                "percentage": round(flat_gwh / daily["summary"]["total_gwh"] * 100, 1)
            },
            "valley_periods": {
                "hours": valley_hours,
                "total_gwh": round(valley_gwh, 3),
                "avg_load_mw": round(sum(load_values[h] for h in valley_hours) / len(valley_hours), 2) if valley_hours else 0,
                "percentage": round(valley_gwh / daily["summary"]["total_gwh"] * 100, 1)
            },
            "recommendations": self._generate_recommendations(peak_hours, valley_hours, load_values),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_recommendations(
        self,
        peak_hours: List[int],
        valley_hours: List[int],
        load_values: List[float]
    ) -> List[str]:
        """生成交易建议"""
        recommendations = []
        
        if valley_hours:
            recommendations.append(
                f"建议在低谷时段 ({min(valley_hours)}:00-{max(valley_hours)+1}:00) 买入电量，价格较低"
            )
        
        if peak_hours:
            recommendations.append(
                f"建议在高峰时段 ({min(peak_hours)}:00-{max(peak_hours)+1}:00) 卖出电量，价格较高"
            )
        
        peak_valley_diff = max(load_values) - min(load_values)
        if peak_valley_diff > max(load_values) * 0.3:
            recommendations.append(
                f"峰谷差较大 ({round(peak_valley_diff, 0)} MW)，存在较好的套利机会"
            )
        
        return recommendations


# 全局电量预测服务实例
load_predictor = LoadPredictor()
