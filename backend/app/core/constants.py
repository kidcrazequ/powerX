"""
PowerX 常量定义

创建日期: 2026-01-07
作者: zhi.qu

系统常量和枚举定义
"""

from enum import Enum


class MarketType(str, Enum):
    """市场类型"""
    DAY_AHEAD = "DAY_AHEAD"      # 日前市场
    INTRADAY = "INTRADAY"        # 日内市场
    MID_LONG = "MID_LONG"        # 中长期市场


class TradingPeriod(str, Enum):
    """交易周期"""
    YEARLY = "YEARLY"            # 年度
    MONTHLY = "MONTHLY"          # 月度
    DAILY = "DAILY"              # 日
    HOURLY = "HOURLY"            # 小时


class Direction(str, Enum):
    """交易方向"""
    BUY = "BUY"                  # 买入
    SELL = "SELL"                # 卖出


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "PENDING"          # 待成交
    PARTIAL = "PARTIAL"          # 部分成交
    FILLED = "FILLED"            # 全部成交
    CANCELLED = "CANCELLED"      # 已撤销


class ContractType(str, Enum):
    """合同类型"""
    YEARLY = "YEARLY"                        # 年度长协
    MONTHLY_BILATERAL = "MONTHLY_BILATERAL"  # 月度双边
    MONTHLY_AUCTION = "MONTHLY_AUCTION"      # 月度竞价


class ContractStatus(str, Enum):
    """合同状态"""
    PENDING = "PENDING"          # 待生效
    ACTIVE = "ACTIVE"            # 执行中
    COMPLETED = "COMPLETED"      # 已完成
    CANCELLED = "CANCELLED"      # 已取消


class ParticipantType(str, Enum):
    """市场主体类型"""
    GENERATOR = "GENERATOR"      # 发电企业
    RETAILER = "RETAILER"        # 售电公司
    LARGE_USER = "LARGE_USER"    # 电力大用户
    GRID = "GRID"                # 电网企业


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "LOW"                  # 低风险
    MEDIUM = "MEDIUM"            # 中风险
    HIGH = "HIGH"                # 高风险
    CRITICAL = "CRITICAL"        # 极高风险


class ReportType(str, Enum):
    """报告类型"""
    DAILY = "DAILY"              # 日报
    WEEKLY = "WEEKLY"            # 周报
    MONTHLY = "MONTHLY"          # 月报
    ANALYSIS = "ANALYSIS"        # 专题分析


# 支持的省份
SUPPORTED_PROVINCES = ["广东", "浙江", "山东", "山西", "甘肃"]

# 限价规则
DEFAULT_PRICE_CAP = {
    "min": 0,
    "max": 1500
}

# 交易时段（小时）
TRADING_HOURS = list(range(24))

# 结算周期（分钟）
SETTLEMENT_PERIODS = [15, 60]
