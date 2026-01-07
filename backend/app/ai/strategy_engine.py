"""
PowerX 策略推荐引擎

创建日期: 2026-01-07
作者: zhi.qu

基于 DeepSeek 的交易策略推荐服务
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.ai.deepseek_client import DeepSeekClient
from app.china_market.provinces import get_province_config
from app.china_market.price_cap import get_base_price


class StrategyEngine:
    """策略推荐引擎"""
    
    def __init__(self):
        self.client = DeepSeekClient()
    
    async def generate_strategy(
        self,
        province: str,
        participant_type: str,
        quantity_mwh: float,
        risk_preference: str = "MEDIUM"
    ) -> Dict:
        """
        生成交易策略
        
        Args:
            province: 省份名称
            participant_type: 参与者类型 (GENERATOR, RETAILER, LARGE_USER)
            quantity_mwh: 交易电量
            risk_preference: 风险偏好 (LOW, MEDIUM, HIGH)
            
        Returns:
            策略推荐
        """
        base_price = get_base_price(province)
        
        # 根据参与者类型和风险偏好生成策略
        strategies = self._generate_strategies(
            province=province,
            participant_type=participant_type,
            quantity_mwh=quantity_mwh,
            risk_preference=risk_preference,
            base_price=base_price
        )
        
        # 生成策略总结
        summary = self._generate_summary(
            province=province,
            participant_type=participant_type,
            quantity_mwh=quantity_mwh,
            risk_preference=risk_preference
        )
        
        return {
            "strategies": strategies,
            "summary": summary
        }
    
    async def generate_strategy_with_ai(
        self,
        province: str,
        participant_type: str,
        quantity_mwh: float,
        risk_preference: str = "MEDIUM",
        market_data: Optional[Dict] = None
    ) -> Dict:
        """
        使用 AI 生成交易策略
        
        Args:
            province: 省份名称
            participant_type: 参与者类型
            quantity_mwh: 交易电量
            risk_preference: 风险偏好
            market_data: 市场数据
            
        Returns:
            AI 策略推荐
        """
        config = get_province_config(province)
        base_price = get_base_price(province)
        
        participant_name = {
            "GENERATOR": "发电企业",
            "RETAILER": "售电公司",
            "LARGE_USER": "电力大用户"
        }.get(participant_type, "交易者")
        
        risk_name = {
            "LOW": "保守型",
            "MEDIUM": "稳健型",
            "HIGH": "激进型"
        }.get(risk_preference, "稳健型")
        
        prompt = f"""你是专业的中国电力交易策略分析师，请为{participant_name}制定{province}省交易策略：

## 市场主体信息
- 类型：{participant_name}
- 月度交易电量：{quantity_mwh} MWh
- 风险偏好：{risk_name}

## 市场数据
- 省份：{province}
- 基准电价：{base_price} 元/MWh
- 价格机制：{config.price_mechanism if config else "统一出清"}

请提供：
1. 建议的中长期锁定比例
2. 现货交易时段建议
3. 报价策略建议
4. 风险控制措施"""

        messages = [
            {"role": "system", "content": "你是专业的电力市场策略分析师，擅长交易策略制定。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat_completion(messages)
        ai_content = response["choices"][0]["message"]["content"]
        
        # 同时返回规则生成的策略
        rule_strategies = await self.generate_strategy(
            province, participant_type, quantity_mwh, risk_preference
        )
        
        return {
            "ai_analysis": ai_content,
            "strategies": rule_strategies["strategies"],
            "summary": rule_strategies["summary"]
        }
    
    def _generate_strategies(
        self,
        province: str,
        participant_type: str,
        quantity_mwh: float,
        risk_preference: str,
        base_price: float
    ) -> List[Dict]:
        """
        生成策略列表
        """
        strategies = []
        
        # 根据风险偏好确定参数
        if risk_preference == "LOW":
            mid_long_ratio = 0.80
            spot_timing = "仅低谷时段"
            confidence = 0.85
        elif risk_preference == "HIGH":
            mid_long_ratio = 0.50
            spot_timing = "全时段灵活操作"
            confidence = 0.65
        else:  # MEDIUM
            mid_long_ratio = 0.70
            spot_timing = "低谷和平段"
            confidence = 0.75
        
        # 策略1：中长期锁定策略
        strategies.append({
            "title": "中长期锁定策略",
            "description": f"建议锁定 {mid_long_ratio*100:.0f}% 的电量在中长期市场",
            "action": f"签订月度双边合同 {quantity_mwh * mid_long_ratio:.0f} MWh，价格区间 {base_price-10:.0f}-{base_price+10:.0f} 元/MWh",
            "confidence": confidence,
            "risk_level": "low" if mid_long_ratio >= 0.7 else "medium"
        })
        
        # 策略2：现货交易策略
        spot_quantity = quantity_mwh * (1 - mid_long_ratio)
        strategies.append({
            "title": "现货套利策略",
            "description": f"利用日内价格波动进行套利，{spot_timing}操作",
            "action": f"在凌晨 0:00-5:00 低谷时段买入 {spot_quantity * 0.6:.0f} MWh",
            "confidence": confidence - 0.1,
            "risk_level": "medium" if risk_preference != "HIGH" else "high"
        })
        
        # 策略3：价差套利（如果适用）
        if province in ["广东", "浙江"]:
            strategies.append({
                "title": "日前-实时价差策略",
                "description": "利用日前与实时市场价差进行套利",
                "action": "日前锁定 70%，实时市场灵活调整 30%",
                "confidence": 0.68,
                "risk_level": "medium"
            })
        
        return strategies
    
    def _generate_summary(
        self,
        province: str,
        participant_type: str,
        quantity_mwh: float,
        risk_preference: str
    ) -> str:
        """
        生成策略总结
        """
        risk_desc = {
            "LOW": "保守稳健",
            "MEDIUM": "平衡风险与收益",
            "HIGH": "追求高收益"
        }.get(risk_preference, "稳健")
        
        return f"基于您的{risk_desc}风险偏好，建议{province}省电量 {quantity_mwh:.0f} MWh 采用" \
               f"中长期为主、现货为辅的组合策略，重点把握低谷时段采购机会。"
