"""
PowerX API v1 路由注册

创建日期: 2026-01-07
作者: zhi.qu

汇总并注册所有 v1 版本 API 路由
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.trading import router as trading_router
from app.api.v1.market import router as market_router
from app.api.v1.contract import router as contract_router
from app.api.v1.settlement import router as settlement_router
from app.api.v1.ai import router as ai_router
from app.api.v1.report import router as report_router
from app.api.v1.ws import router as ws_router
from app.api.v1.audit import router as audit_router
from app.api.v1.admin import router as admin_router
from app.api.v1.alert import router as alert_router
from app.api.v1.data import router as data_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.simulation import router as simulation_router
from app.api.v1.conditional_order import router as conditional_order_router
from app.api.v1.trading_rule import router as trading_rule_router
from app.api.v1.ai_advisor import router as ai_advisor_router
from app.api.v1.health import router as health_router
from app.api.v1.limits import router as limits_router
from app.api.v1.approval import router as approval_router
from app.api.v1.notification import router as notification_router
from app.api.v1.backup import router as backup_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.report_builder import router as report_builder_router
from app.api.v1.history import router as history_router
from app.api.v1.combo_order import router as combo_order_router
from app.api.v1.algo_trading import router as algo_trading_router
from app.api.v1.cross_province import router as cross_province_router
from app.api.v1.webhook import router as webhook_router
from app.api.v1.option import router as option_router
from app.api.v1.signature import router as signature_router
from app.api.v1.open_api import router as open_api_router

# 创建 v1 API 主路由
api_router = APIRouter()

# 注册各模块路由
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["认证"]
)

api_router.include_router(
    trading_router,
    prefix="/trading",
    tags=["交易"]
)

api_router.include_router(
    market_router,
    prefix="/market",
    tags=["市场数据"]
)

api_router.include_router(
    contract_router,
    prefix="/contracts",
    tags=["合同管理"]
)

api_router.include_router(
    settlement_router,
    prefix="/settlement",
    tags=["结算"]
)

api_router.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI服务"]
)

api_router.include_router(
    report_router,
    prefix="/reports",
    tags=["报告"]
)

api_router.include_router(
    ws_router,
    prefix="/ws",
    tags=["WebSocket"]
)

api_router.include_router(
    audit_router,
    prefix="/audit",
    tags=["审计日志"]
)

api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["系统管理"]
)

api_router.include_router(
    alert_router,
    prefix="/alerts",
    tags=["预警管理"]
)

api_router.include_router(
    data_router,
    prefix="/data",
    tags=["数据导入导出"]
)

api_router.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["数据分析"]
)

api_router.include_router(
    forecast_router,
    prefix="/forecast",
    tags=["电量预测"]
)

api_router.include_router(
    simulation_router,
    prefix="/simulation",
    tags=["交易模拟"]
)

api_router.include_router(
    conditional_order_router,
    prefix="/conditional-orders",
    tags=["条件单"]
)

api_router.include_router(
    trading_rule_router,
    prefix="/trading-rules",
    tags=["交易规则"]
)

api_router.include_router(
    ai_advisor_router,
    prefix="/ai-advisor",
    tags=["AI顾问"]
)

api_router.include_router(health_router, prefix="/health", tags=["系统健康"])
api_router.include_router(limits_router, prefix="/limits", tags=["交易限额"])
api_router.include_router(approval_router, prefix="/approval", tags=["审批流程"])
api_router.include_router(notification_router, prefix="/notifications", tags=["通知管理"])
api_router.include_router(backup_router, prefix="/backup", tags=["备份管理"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(report_builder_router, prefix="/report-builder", tags=["报表生成器"])
api_router.include_router(history_router, prefix="/history", tags=["历史回放"])
api_router.include_router(combo_order_router, prefix="/combo-orders", tags=["组合订单"])
api_router.include_router(algo_trading_router, prefix="/algo-trading", tags=["算法交易"])
api_router.include_router(cross_province_router, prefix="/cross-province", tags=["跨省交易"])
api_router.include_router(webhook_router, prefix="/webhooks", tags=["Webhook"])
api_router.include_router(option_router, prefix="/options", tags=["期权交易"])
api_router.include_router(signature_router, prefix="/signatures", tags=["电子签章"])
api_router.include_router(open_api_router, prefix="/open-api", tags=["开放API"])