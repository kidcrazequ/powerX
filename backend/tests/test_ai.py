"""
PowerX AI 模块测试

创建日期: 2026-01-07
作者: zhi.qu

测试 AI 相关功能
"""

import pytest


class TestPricePredictor:
    """价格预测器测试"""
    
    @pytest.mark.asyncio
    async def test_predict_guangdong(self):
        """测试广东价格预测"""
        from app.ai.price_predictor import PricePredictor
        
        predictor = PricePredictor()
        result = await predictor.predict(
            province="广东",
            market_type="DAY_AHEAD",
            hours=24
        )
        
        assert "predictions" in result
        assert "summary" in result
        assert "confidence" in result
        assert len(result["predictions"]) == 24
    
    @pytest.mark.asyncio
    async def test_predict_shandong_negative_price(self):
        """测试山东负电价预测"""
        from app.ai.price_predictor import PricePredictor
        
        predictor = PricePredictor()
        result = await predictor.predict(
            province="山东",
            market_type="DAY_AHEAD",
            hours=24
        )
        
        # 山东可能出现负电价
        prices = [p["price"] for p in result["predictions"]]
        min_price = min(prices)
        
        # 最低价可能为负
        assert min_price <= 100  # 低于基准价较多


class TestStrategyEngine:
    """策略引擎测试"""
    
    @pytest.mark.asyncio
    async def test_generate_strategy_low_risk(self):
        """测试低风险策略生成"""
        from app.ai.strategy_engine import StrategyEngine
        
        engine = StrategyEngine()
        result = await engine.generate_strategy(
            province="广东",
            participant_type="RETAILER",
            quantity_mwh=10000,
            risk_preference="LOW"
        )
        
        assert "strategies" in result
        assert "summary" in result
        assert len(result["strategies"]) > 0
        
        # 低风险策略应该有较高的中长期锁定比例
        first_strategy = result["strategies"][0]
        assert first_strategy["risk_level"] in ["low", "medium"]
    
    @pytest.mark.asyncio
    async def test_generate_strategy_high_risk(self):
        """测试高风险策略生成"""
        from app.ai.strategy_engine import StrategyEngine
        
        engine = StrategyEngine()
        result = await engine.generate_strategy(
            province="广东",
            participant_type="RETAILER",
            quantity_mwh=10000,
            risk_preference="HIGH"
        )
        
        assert "strategies" in result
        assert len(result["strategies"]) > 0


class TestQAAssistant:
    """问答助手测试"""
    
    @pytest.mark.asyncio
    async def test_answer_policy_question(self):
        """测试政策问题回答"""
        from app.ai.qa_assistant import QAAssistant
        
        assistant = QAAssistant()
        answer = await assistant.answer_question(
            question="广东省电力市场有什么特点？"
        )
        
        assert answer is not None
        assert len(answer) > 0
        assert "广东" in answer
    
    @pytest.mark.asyncio
    async def test_answer_trading_question(self):
        """测试交易问题回答"""
        from app.ai.qa_assistant import QAAssistant
        
        assistant = QAAssistant()
        answer = await assistant.answer_question(
            question="什么是中长期交易？"
        )
        
        assert answer is not None
        assert len(answer) > 0


class TestReportGenerator:
    """报告生成器测试"""
    
    @pytest.mark.asyncio
    async def test_generate_daily_report(self):
        """测试日报生成"""
        from app.ai.report_generator import ReportGenerator
        from datetime import date
        
        generator = ReportGenerator()
        result = await generator.generate(
            report_type="DAILY",
            target_date=date.today()
        )
        
        assert "id" in result
        assert "title" in result
        assert "content" in result
        assert "DAILY" in result["report_type"] or "日报" in result["title"]
    
    @pytest.mark.asyncio
    async def test_generate_weekly_report(self):
        """测试周报生成"""
        from app.ai.report_generator import ReportGenerator
        from datetime import date
        
        generator = ReportGenerator()
        result = await generator.generate(
            report_type="WEEKLY",
            target_date=date.today()
        )
        
        assert "id" in result
        assert "content" in result
        assert len(result["content"]) > 100  # 内容应该有一定长度
