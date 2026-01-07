"""
PowerX 电量预测服务

创建日期: 2026-01-07
作者: zhi.qu

提供日/周/月电量和负荷曲线预测功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from loguru import logger
import random
import math


class ForecastService:
    """电量预测服务"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化预测服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        logger.info("ForecastService 初始化完成")
    
    async def get_daily_load_curve(
        self,
        province: str,
        target_date: date
    ) -> Dict[str, Any]:
        """
        获取日负荷曲线预测
        
        Args:
            province: 省份
            target_date: 目标日期
            
        Returns:
            包含24小时负荷和电量预测的字典
        """
        logger.info(f"获取 {province} {target_date} 日负荷曲线预测")
        
        # 典型负荷曲线模式 (0-23时的负荷因子)
        load_pattern = [
            0.65, 0.60, 0.55, 0.52, 0.50, 0.55,  # 00:00-05:00 低谷
            0.65, 0.80, 0.95, 1.00, 0.98, 0.95,  # 06:00-11:00 早高峰
            0.90, 0.92, 0.95, 0.98, 1.00, 1.05,  # 12:00-17:00 午间平段
            1.10, 1.08, 1.00, 0.90, 0.80, 0.70   # 18:00-23:00 晚高峰
        ]
        
        # 根据省份调整基准负荷 (MW)
        base_loads = {
            "guangdong": 120000,
            "zhejiang": 85000,
            "jiangsu": 95000,
            "shandong": 90000,
            "sichuan": 60000
        }
        base_load = base_loads.get(province, 80000)
        
        # 工作日/周末因子
        weekday = target_date.weekday()
        weekday_factor = 0.75 if weekday >= 5 else 1.0
        
        # 生成24小时数据
        hourly_data = []
        for hour in range(24):
            # 加入随机波动
            noise = random.uniform(-0.02, 0.02)
            load = int(base_load * load_pattern[hour] * weekday_factor * (1 + noise))
            energy = round(load / 1000, 2)  # GWh
            
            hourly_data.append({
                "hour": hour,
                "time": f"{hour:02d}:00",
                "load": load,
                "energy": energy,
                "load_factor": round(load_pattern[hour] * weekday_factor, 3)
            })
        
        # 计算统计信息
        loads = [d["load"] for d in hourly_data]
        total_energy = sum(d["energy"] for d in hourly_data)
        
        return {
            "province": province,
            "date": target_date.isoformat(),
            "hourly_data": hourly_data,
            "statistics": {
                "total_energy": round(total_energy, 2),
                "peak_load": max(loads),
                "valley_load": min(loads),
                "average_load": round(sum(loads) / len(loads)),
                "peak_valley_ratio": round(max(loads) / min(loads), 2),
                "peak_hour": loads.index(max(loads)),
                "valley_hour": loads.index(min(loads))
            }
        }
    
    async def get_weekly_forecast(
        self,
        province: str,
        start_date: date
    ) -> Dict[str, Any]:
        """
        获取周电量预测
        
        Args:
            province: 省份
            start_date: 起始日期
            
        Returns:
            包含7天电量预测的字典
        """
        logger.info(f"获取 {province} {start_date} 周电量预测")
        
        # 周模式因子 (周一到周日)
        weekly_pattern = [1.0, 1.02, 1.01, 1.0, 0.98, 0.75, 0.70]
        
        # 基准日电量 (GWh)
        base_energies = {
            "guangdong": 2800,
            "zhejiang": 2000,
            "jiangsu": 2200,
            "shandong": 2100,
            "sichuan": 1400
        }
        base_energy = base_energies.get(province, 1800)
        
        daily_data = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            weekday = current_date.weekday()
            
            # 加入随机波动
            noise = random.uniform(-0.03, 0.03)
            energy = round(base_energy * weekly_pattern[weekday] * (1 + noise), 1)
            
            daily_data.append({
                "date": current_date.isoformat(),
                "weekday": weekday,
                "weekday_name": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday],
                "energy": energy,
                "factor": weekly_pattern[weekday]
            })
        
        # 统计
        energies = [d["energy"] for d in daily_data]
        
        return {
            "province": province,
            "start_date": start_date.isoformat(),
            "end_date": (start_date + timedelta(days=6)).isoformat(),
            "daily_data": daily_data,
            "statistics": {
                "total_energy": round(sum(energies), 1),
                "average_energy": round(sum(energies) / len(energies), 1),
                "max_energy": max(energies),
                "min_energy": min(energies)
            }
        }
    
    async def get_monthly_forecast(
        self,
        province: str,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        获取月电量预测
        
        Args:
            province: 省份
            year: 年份
            month: 月份
            
        Returns:
            包含当月每日电量预测的字典
        """
        logger.info(f"获取 {province} {year}-{month:02d} 月电量预测")
        
        # 计算当月天数
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        days_in_month = (next_month - date(year, month, 1)).days
        
        # 周模式因子
        weekly_pattern = [1.0, 1.02, 1.01, 1.0, 0.98, 0.75, 0.70]
        
        # 季节因子 (夏季和冬季用电量高)
        seasonal_factors = {
            1: 1.05, 2: 0.95, 3: 0.90, 4: 0.85,
            5: 0.90, 6: 1.00, 7: 1.10, 8: 1.15,
            9: 1.05, 10: 0.95, 11: 0.95, 12: 1.05
        }
        seasonal_factor = seasonal_factors.get(month, 1.0)
        
        # 基准日电量 (GWh)
        base_energies = {
            "guangdong": 2800,
            "zhejiang": 2000,
            "jiangsu": 2200,
            "shandong": 2100,
            "sichuan": 1400
        }
        base_energy = base_energies.get(province, 1800)
        
        daily_data = []
        for day in range(1, days_in_month + 1):
            current_date = date(year, month, day)
            weekday = current_date.weekday()
            
            # 加入随机波动
            noise = random.uniform(-0.04, 0.04)
            energy = round(
                base_energy * weekly_pattern[weekday] * seasonal_factor * (1 + noise),
                1
            )
            
            daily_data.append({
                "date": current_date.isoformat(),
                "day": day,
                "weekday": weekday,
                "energy": energy
            })
        
        # 统计
        energies = [d["energy"] for d in daily_data]
        
        return {
            "province": province,
            "year": year,
            "month": month,
            "days_in_month": days_in_month,
            "daily_data": daily_data,
            "statistics": {
                "total_energy": round(sum(energies), 1),
                "average_energy": round(sum(energies) / len(energies), 1),
                "max_energy": max(energies),
                "min_energy": min(energies),
                "seasonal_factor": seasonal_factor
            }
        }
    
    async def get_peak_valley_analysis(
        self,
        province: str,
        target_date: date
    ) -> Dict[str, Any]:
        """
        获取峰谷时段分析
        
        Args:
            province: 省份
            target_date: 目标日期
            
        Returns:
            峰谷时段分析结果
        """
        logger.info(f"获取 {province} {target_date} 峰谷时段分析")
        
        # 获取日负荷曲线
        daily_curve = await self.get_daily_load_curve(province, target_date)
        hourly_data = daily_curve["hourly_data"]
        
        # 定义峰谷时段 (可配置化)
        peak_hours = [10, 11, 18, 19, 20]
        valley_hours = [0, 1, 2, 3, 4, 5, 6, 23]
        flat_hours = [h for h in range(24) if h not in peak_hours and h not in valley_hours]
        
        # 计算各时段数据
        peak_loads = [hourly_data[h]["load"] for h in peak_hours]
        valley_loads = [hourly_data[h]["load"] for h in valley_hours]
        flat_loads = [hourly_data[h]["load"] for h in flat_hours]
        
        total_energy = sum(d["energy"] for d in hourly_data)
        peak_energy = sum(hourly_data[h]["energy"] for h in peak_hours)
        valley_energy = sum(hourly_data[h]["energy"] for h in valley_hours)
        flat_energy = sum(hourly_data[h]["energy"] for h in flat_hours)
        
        return {
            "province": province,
            "date": target_date.isoformat(),
            "peak": {
                "hours": peak_hours,
                "avg_load": round(sum(peak_loads) / len(peak_loads)),
                "max_load": max(peak_loads),
                "energy": round(peak_energy, 2),
                "percentage": round(peak_energy / total_energy * 100, 1)
            },
            "valley": {
                "hours": valley_hours,
                "avg_load": round(sum(valley_loads) / len(valley_loads)),
                "min_load": min(valley_loads),
                "energy": round(valley_energy, 2),
                "percentage": round(valley_energy / total_energy * 100, 1)
            },
            "flat": {
                "hours": flat_hours,
                "avg_load": round(sum(flat_loads) / len(flat_loads)),
                "energy": round(flat_energy, 2),
                "percentage": round(flat_energy / total_energy * 100, 1)
            },
            "recommendations": [
                "建议在低谷时段买入电量，价格较低",
                "建议在高峰时段卖出电量，价格较高",
                f"峰谷价差预估约 {round(max(peak_loads) * 0.004 - min(valley_loads) * 0.003, 2)} 元/MWh"
            ]
        }
