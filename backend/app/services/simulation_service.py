"""
PowerX 交易模拟/回测服务

创建日期: 2026-01-07
作者: zhi.qu

提供策略回测和模拟交易功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from loguru import logger
import random
import math
import json

from app.models.simulation import SimulationSession, SimulationTrade, SimulationStatus


class SimulationService:
    """交易模拟/回测服务"""
    
    # 可用策略
    AVAILABLE_STRATEGIES = {
        "mean_reversion": {
            "name": "均值回归",
            "description": "当价格偏离均值一定幅度时进行反向交易",
            "params": {
                "window": {"type": "int", "default": 20, "description": "均值计算窗口"},
                "threshold": {"type": "float", "default": 2.0, "description": "标准差倍数阈值"}
            }
        },
        "momentum": {
            "name": "动量策略",
            "description": "跟随价格趋势进行交易",
            "params": {
                "fast_period": {"type": "int", "default": 5, "description": "快速均线周期"},
                "slow_period": {"type": "int", "default": 20, "description": "慢速均线周期"}
            }
        },
        "breakout": {
            "name": "突破策略",
            "description": "当价格突破区间时进行交易",
            "params": {
                "lookback": {"type": "int", "default": 20, "description": "回顾周期"},
                "multiplier": {"type": "float", "default": 1.5, "description": "突破幅度倍数"}
            }
        },
        "arbitrage": {
            "name": "跨省套利",
            "description": "利用省间价差进行套利交易",
            "params": {
                "spread_threshold": {"type": "float", "default": 30.0, "description": "价差阈值 (元/MWh)"},
                "max_position": {"type": "float", "default": 1000.0, "description": "最大持仓 (MWh)"}
            }
        },
        "peak_valley": {
            "name": "峰谷套利",
            "description": "低谷买入、高峰卖出",
            "params": {
                "buy_hours": {"type": "list", "default": [0, 1, 2, 3, 4, 5], "description": "买入时段"},
                "sell_hours": {"type": "list", "default": [18, 19, 20, 21], "description": "卖出时段"}
            }
        }
    }
    
    def __init__(self, db: AsyncSession):
        """
        初始化服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        logger.info("SimulationService 初始化完成")
    
    async def get_available_strategies(self) -> Dict[str, Any]:
        """获取可用策略列表"""
        return self.AVAILABLE_STRATEGIES
    
    async def create_backtest(
        self,
        user_id: str,
        name: str,
        strategy_name: str,
        start_date: date,
        end_date: date,
        strategy_params: Optional[Dict[str, Any]] = None,
        initial_capital: float = 1000000.0,
        description: Optional[str] = None
    ) -> SimulationSession:
        """
        创建回测任务
        
        Args:
            user_id: 用户ID
            name: 回测名称
            strategy_name: 策略名称
            start_date: 开始日期
            end_date: 结束日期
            strategy_params: 策略参数
            initial_capital: 初始资金
            description: 描述
            
        Returns:
            创建的回测会话
        """
        if strategy_name not in self.AVAILABLE_STRATEGIES:
            raise ValueError(f"未知策略: {strategy_name}")
        
        session = SimulationSession(
            user_id=user_id,
            name=name,
            description=description,
            simulation_type="BACKTEST",
            strategy_name=strategy_name,
            strategy_params=strategy_params or {},
            start_date=datetime.combine(start_date, datetime.min.time()),
            end_date=datetime.combine(end_date, datetime.max.time()),
            initial_capital=initial_capital,
            status=SimulationStatus.PENDING.value
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info(f"创建回测任务: {name} (ID: {session.id})")
        return session
    
    async def run_backtest(self, session_id: int) -> SimulationSession:
        """
        执行回测
        
        Args:
            session_id: 回测会话ID
            
        Returns:
            更新后的回测会话
        """
        session = await self.db.get(SimulationSession, session_id)
        if not session:
            raise ValueError(f"回测会话不存在: {session_id}")
        
        if session.status != SimulationStatus.PENDING.value:
            raise ValueError(f"回测会话状态不正确: {session.status}")
        
        # 更新状态为运行中
        session.status = SimulationStatus.RUNNING.value
        session.started_at = datetime.now()
        await self.db.commit()
        
        logger.info(f"开始执行回测: {session.name} (ID: {session.id})")
        
        try:
            # 生成模拟价格数据
            prices = self._generate_mock_prices(session.start_date, session.end_date)
            
            # 执行策略
            trades, equity_curve = await self._execute_strategy(
                session, prices
            )
            
            # 保存交易记录
            for trade_data in trades:
                trade = SimulationTrade(
                    session_id=session.id,
                    **trade_data
                )
                self.db.add(trade)
            
            # 计算统计指标
            stats = self._calculate_statistics(
                initial_capital=session.initial_capital,
                trades=trades,
                equity_curve=equity_curve
            )
            
            # 更新会话结果
            session.status = SimulationStatus.COMPLETED.value
            session.completed_at = datetime.now()
            session.progress = 100.0
            session.final_capital = stats["final_capital"]
            session.total_return = stats["total_return"]
            session.annual_return = stats["annual_return"]
            session.max_drawdown = stats["max_drawdown"]
            session.sharpe_ratio = stats["sharpe_ratio"]
            session.win_rate = stats["win_rate"]
            session.total_trades = stats["total_trades"]
            session.result_data = {
                "equity_curve": equity_curve,
                "statistics": stats
            }
            
            await self.db.commit()
            await self.db.refresh(session)
            
            logger.info(f"回测完成: {session.name}, 收益率: {stats['total_return']:.2%}")
            return session
            
        except Exception as e:
            logger.error(f"回测执行失败: {e}")
            session.status = SimulationStatus.FAILED.value
            session.error_message = str(e)
            await self.db.commit()
            raise
    
    async def get_user_sessions(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[SimulationSession]:
        """
        获取用户的回测会话列表
        
        Args:
            user_id: 用户ID
            status: 状态过滤
            limit: 返回数量限制
            
        Returns:
            回测会话列表
        """
        query = select(SimulationSession).where(
            SimulationSession.user_id == user_id
        )
        
        if status:
            query = query.where(SimulationSession.status == status)
        
        query = query.order_by(desc(SimulationSession.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_session_detail(self, session_id: int) -> Optional[SimulationSession]:
        """获取回测会话详情"""
        return await self.db.get(SimulationSession, session_id)
    
    async def get_session_trades(self, session_id: int) -> List[SimulationTrade]:
        """获取回测会话的交易记录"""
        query = select(SimulationTrade).where(
            SimulationTrade.session_id == session_id
        ).order_by(SimulationTrade.trade_time)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def delete_session(self, session_id: int) -> bool:
        """删除回测会话"""
        session = await self.db.get(SimulationSession, session_id)
        if session:
            await self.db.delete(session)
            await self.db.commit()
            logger.info(f"删除回测会话: {session_id}")
            return True
        return False
    
    # ============ 私有方法 ============
    
    def _generate_mock_prices(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """生成模拟价格数据"""
        prices = []
        current_date = start_date
        base_price = 450.0
        
        while current_date <= end_date:
            # 添加趋势和波动
            days_passed = (current_date - start_date).days
            trend = math.sin(days_passed / 30 * math.pi) * 20  # 周期性趋势
            noise = random.gauss(0, 15)  # 随机波动
            
            price = base_price + trend + noise
            
            prices.append({
                "date": current_date,
                "price": round(max(price, 300), 2),  # 最低价300
                "volume": random.randint(50000, 150000)
            })
            
            current_date += timedelta(days=1)
        
        return prices
    
    async def _execute_strategy(
        self,
        session: SimulationSession,
        prices: List[Dict[str, Any]]
    ) -> tuple:
        """
        执行交易策略
        
        Returns:
            (交易列表, 权益曲线)
        """
        trades = []
        equity_curve = []
        
        capital = session.initial_capital
        position = 0.0  # 当前持仓
        position_cost = 0.0  # 持仓成本
        
        strategy = session.strategy_name
        params = session.strategy_params or {}
        
        for i, price_data in enumerate(prices):
            current_price = price_data["price"]
            current_date = price_data["date"]
            
            # 更新进度
            session.progress = (i + 1) / len(prices) * 100
            
            # 根据策略生成信号
            signal = self._generate_signal(
                strategy, params, prices[:i+1], position
            )
            
            # 执行交易
            if signal == "BUY" and position == 0:
                # 买入 (使用80%资金)
                quantity = (capital * 0.8) / current_price
                amount = quantity * current_price
                commission = amount * 0.001  # 0.1% 手续费
                
                position = quantity
                position_cost = current_price
                capital -= (amount + commission)
                
                trades.append({
                    "trade_time": current_date,
                    "direction": "BUY",
                    "price": current_price,
                    "quantity": round(quantity, 2),
                    "amount": round(amount, 2),
                    "commission": round(commission, 2),
                    "signal": f"{strategy}_{signal}"
                })
                
            elif signal == "SELL" and position > 0:
                # 卖出
                amount = position * current_price
                commission = amount * 0.001
                profit = (current_price - position_cost) * position - commission
                profit_rate = (current_price - position_cost) / position_cost
                
                capital += (amount - commission)
                
                trades.append({
                    "trade_time": current_date,
                    "direction": "SELL",
                    "price": current_price,
                    "quantity": round(position, 2),
                    "amount": round(amount, 2),
                    "commission": round(commission, 2),
                    "profit": round(profit, 2),
                    "profit_rate": round(profit_rate, 4),
                    "signal": f"{strategy}_{signal}"
                })
                
                position = 0
                position_cost = 0
            
            # 记录权益曲线
            equity = capital + position * current_price
            equity_curve.append({
                "date": current_date.isoformat(),
                "equity": round(equity, 2),
                "capital": round(capital, 2),
                "position_value": round(position * current_price, 2)
            })
        
        return trades, equity_curve
    
    def _generate_signal(
        self,
        strategy: str,
        params: Dict[str, Any],
        prices: List[Dict[str, Any]],
        position: float
    ) -> Optional[str]:
        """生成交易信号"""
        if len(prices) < 2:
            return None
        
        current_price = prices[-1]["price"]
        
        if strategy == "mean_reversion":
            window = params.get("window", 20)
            threshold = params.get("threshold", 2.0)
            
            if len(prices) < window:
                return None
            
            recent_prices = [p["price"] for p in prices[-window:]]
            mean = sum(recent_prices) / len(recent_prices)
            std = (sum((p - mean) ** 2 for p in recent_prices) / len(recent_prices)) ** 0.5
            
            if std > 0:
                z_score = (current_price - mean) / std
                if z_score < -threshold and position == 0:
                    return "BUY"
                elif z_score > threshold and position > 0:
                    return "SELL"
                    
        elif strategy == "momentum":
            fast_period = params.get("fast_period", 5)
            slow_period = params.get("slow_period", 20)
            
            if len(prices) < slow_period:
                return None
            
            fast_ma = sum(p["price"] for p in prices[-fast_period:]) / fast_period
            slow_ma = sum(p["price"] for p in prices[-slow_period:]) / slow_period
            prev_fast = sum(p["price"] for p in prices[-fast_period-1:-1]) / fast_period
            prev_slow = sum(p["price"] for p in prices[-slow_period-1:-1]) / slow_period
            
            # 金叉买入，死叉卖出
            if prev_fast <= prev_slow and fast_ma > slow_ma and position == 0:
                return "BUY"
            elif prev_fast >= prev_slow and fast_ma < slow_ma and position > 0:
                return "SELL"
                
        elif strategy == "breakout":
            lookback = params.get("lookback", 20)
            
            if len(prices) < lookback:
                return None
            
            recent_prices = [p["price"] for p in prices[-lookback:-1]]
            high = max(recent_prices)
            low = min(recent_prices)
            
            if current_price > high and position == 0:
                return "BUY"
            elif current_price < low and position > 0:
                return "SELL"
        
        elif strategy == "peak_valley":
            # 简化的峰谷策略 (基于随机模拟)
            hour = prices[-1]["date"].hour if hasattr(prices[-1]["date"], "hour") else 12
            
            if hour < 6 and position == 0 and random.random() > 0.7:
                return "BUY"
            elif hour > 17 and position > 0 and random.random() > 0.7:
                return "SELL"
        
        elif strategy == "arbitrage":
            # 简化的套利策略
            if len(prices) >= 2:
                price_change = current_price - prices[-2]["price"]
                if price_change < -params.get("spread_threshold", 30) and position == 0:
                    return "BUY"
                elif price_change > params.get("spread_threshold", 30) and position > 0:
                    return "SELL"
        
        return None
    
    def _calculate_statistics(
        self,
        initial_capital: float,
        trades: List[Dict[str, Any]],
        equity_curve: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算回测统计指标"""
        if not equity_curve:
            return {
                "final_capital": initial_capital,
                "total_return": 0.0,
                "annual_return": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "win_rate": 0.0,
                "total_trades": 0
            }
        
        final_capital = equity_curve[-1]["equity"]
        total_return = (final_capital - initial_capital) / initial_capital
        
        # 计算年化收益
        days = len(equity_curve)
        annual_return = ((1 + total_return) ** (365 / max(days, 1))) - 1
        
        # 计算最大回撤
        peak = initial_capital
        max_drawdown = 0.0
        for point in equity_curve:
            equity = point["equity"]
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 计算每日收益率和夏普比率
        returns = []
        for i in range(1, len(equity_curve)):
            prev_equity = equity_curve[i-1]["equity"]
            curr_equity = equity_curve[i]["equity"]
            if prev_equity > 0:
                returns.append((curr_equity - prev_equity) / prev_equity)
        
        if returns:
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe_ratio = (avg_return * 252) / (std_return * (252 ** 0.5)) if std_return > 0 else 0
        else:
            sharpe_ratio = 0.0
        
        # 计算胜率
        winning_trades = [t for t in trades if t.get("profit", 0) > 0]
        sell_trades = [t for t in trades if t["direction"] == "SELL"]
        win_rate = len(winning_trades) / len(sell_trades) if sell_trades else 0.0
        
        return {
            "final_capital": round(final_capital, 2),
            "total_return": round(total_return, 4),
            "annual_return": round(annual_return, 4),
            "max_drawdown": round(max_drawdown, 4),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "win_rate": round(win_rate, 4),
            "total_trades": len(trades)
        }


# 单例服务实例
simulation_service = SimulationService(None)
