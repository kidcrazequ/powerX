"""
PowerX 电价预测模块

创建日期: 2026-01-07
作者: zhi.qu

基于 DeepSeek 的电价预测服务
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.ai.deepseek_client import DeepSeekClient
from app.china_market.provinces import get_province_config
from app.china_market.price_cap import get_price_limits, get_base_price


class PricePredictor:
    """电价预测器"""
    
    # 24小时价格模式
    HOURLY_PATTERN = [
        0.92, 0.88, 0.85, 0.82, 0.84, 0.86,
        0.94, 1.03, 1.06, 1.08, 1.06, 1.04,
        1.02, 1.00, 0.98, 1.02, 1.08, 1.06,
        1.04, 1.02, 0.98, 0.95, 0.92, 0.88
    ]
    
    def __init__(self):
        self.client = DeepSeekClient()
    
    async def predict(
        self,
        province: str,
        market_type: str = "DAY_AHEAD",
        hours: int = 24
    ) -> Dict:
        """
        预测电价
        
        Args:
            province: 省份名称
            market_type: 市场类型
            hours: 预测小时数
            
        Returns:
            预测结果
        """
        base_price = get_base_price(province)
        min_price, max_price = get_price_limits(province)
        
        predictions = []
        current_hour = datetime.now().hour
        
        for i in range(hours):
            hour = (current_hour + i + 1) % 24
            
            # 基于模式生成预测价格
            pattern_factor = self.HOURLY_PATTERN[hour]
            predicted_price = base_price * pattern_factor
            
            # 添加随机波动
            predicted_price += random.uniform(-15, 15)
            
            # 山东允许负电价
            if province == "山东" and hour in [3, 4, 5] and random.random() < 0.15:
                predicted_price = random.uniform(-30, 50)
            
            # 限价约束
            predicted_price = max(min_price, min(max_price, predicted_price))
            
            # 置信度随时间递减
            confidence = max(0.5, 0.95 - i * 0.02)
            
            predictions.append({
                "hour": f"{hour:02d}:00",
                "price": round(predicted_price, 2),
                "confidence": round(confidence, 2),
                "range_low": round(predicted_price * 0.95, 2),
                "range_high": round(predicted_price * 1.05, 2)
            })
        
        # 生成预测总结
        avg_price = sum(p["price"] for p in predictions) / len(predictions)
        max_pred = max(p["price"] for p in predictions)
        min_pred = min(p["price"] for p in predictions)
        peak_hour = max(predictions, key=lambda x: x["price"])["hour"]
        
        summary = self._generate_summary(province, avg_price, max_pred, min_pred, peak_hour)
        
        return {
            "predictions": predictions,
            "summary": summary,
            "confidence": round(sum(p["confidence"] for p in predictions) / len(predictions), 2)
        }
    
    async def predict_with_ai(
        self,
        province: str,
        market_type: str = "DAY_AHEAD",
        historical_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        使用 AI 进行电价预测
        
        Args:
            province: 省份名称
            market_type: 市场类型
            historical_data: 历史数据
            
        Returns:
            AI 预测结果
        """
        config = get_province_config(province)
        min_price, max_price = get_price_limits(province)
        
        # 构建提示词
        prompt = f"""你是一位专业的中国电力现货市场分析师，请基于以下信息预测{province}省未来24小时的日前现货电价：

## 省份特征
- 省份：{province}
- 价格机制：{config.price_mechanism if config else "统一出清"}
- 限价范围：{min_price} - {max_price} 元/MWh
- 新能源占比：{config.renewable_ratio * 100 if config else 20}%

## 当前市场状态
- 当前时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}
- 基准电价：{get_base_price(province)} 元/MWh

请以JSON格式输出预测结果。"""

        messages = [
            {"role": "system", "content": "你是专业的电力市场分析师，擅长电价预测和市场分析。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat_completion(messages)
        
        # 解析 AI 响应
        ai_content = response["choices"][0]["message"]["content"]
        
        # 同时返回规则预测结果
        rule_prediction = await self.predict(province, market_type, 24)
        
        return {
            "ai_analysis": ai_content,
            "predictions": rule_prediction["predictions"],
            "summary": rule_prediction["summary"],
            "confidence": rule_prediction["confidence"]
        }
    
    def _generate_summary(
        self,
        province: str,
        avg_price: float,
        max_price: float,
        min_price: float,
        peak_hour: str
    ) -> str:
        """
        生成预测总结
        
        Args:
            province: 省份
            avg_price: 均价
            max_price: 最高价
            min_price: 最低价
            peak_hour: 峰值时段
            
        Returns:
            总结文本
        """
        base = get_base_price(province)
        trend = "上涨" if avg_price > base else "下跌" if avg_price < base else "持平"
        
        return f"预计{province}省未来24小时电价{trend}，均价约 {avg_price:.2f} 元/MWh，" \
               f"峰值出现在 {peak_hour} 左右（约 {max_price:.2f} 元/MWh），" \
               f"建议在凌晨低谷时段（{min_price:.2f} 元/MWh）增加采购。"
