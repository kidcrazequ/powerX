"""
PowerX 电力交易系统主入口

创建日期: 2026-01-07
作者: zhi.qu

FastAPI 应用主入口，配置中间件、路由、生命周期事件等
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger
import sys
import traceback

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.exceptions import (
    PowerXException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ExternalServiceError
)
from app.api.v1 import api_router
from app.services.realtime_service import realtime_service


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL,
    colorize=True
)
logger.add(
    "logs/powerx_{time:YYYY-MM-DD}.log",
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL,
    rotation="00:00",
    retention="30 days",
    compression="gz"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    处理应用启动和关闭时的初始化和清理工作
    """
    # 启动时执行
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info(f"默认省份: {settings.DEFAULT_PROVINCE}")
    logger.info(f"数据库URL: {settings.DATABASE_URL}")
    
    # 初始化数据库（捕获错误以便在没有数据库时也能启动）
    try:
        await init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.warning(f"数据库初始化失败: {e}，应用将继续运行但数据库功能不可用")
    
    # 启动实时数据推送服务
    try:
        await realtime_service.start()
        logger.info("实时数据服务启动成功")
    except Exception as e:
        logger.warning(f"实时数据服务启动失败: {e}")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭应用...")
    
    # 停止实时数据服务
    try:
        await realtime_service.stop()
        logger.info("实时数据服务已停止")
    except Exception as e:
        logger.warning(f"停止实时数据服务失败: {e}")
    
    # 关闭数据库连接
    try:
        await close_db()
    except Exception as e:
        logger.warning(f"关闭数据库连接失败: {e}")
    
    logger.info("应用已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 全局异常处理器 ============

@app.exception_handler(PowerXException)
async def powerx_exception_handler(request: Request, exc: PowerXException):
    """处理 PowerX 自定义异常"""
    logger.warning(f"PowerX异常: {exc.message} | 路径: {request.url.path}")
    return JSONResponse(
        status_code=exc.code,
        content=exc.to_dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"请求验证失败: {errors} | 路径: {request.url.path}")
    return JSONResponse(
        status_code=400,
        content={
            "code": 400,
            "message": "请求参数验证失败",
            "success": False,
            "detail": errors
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理 HTTP 异常"""
    message_map = {
        400: "请求无效",
        401: "未认证，请先登录",
        403: "权限不足",
        404: "请求的资源不存在",
        405: "请求方法不允许",
        429: "请求过于频繁",
        500: "服务器内部错误",
        502: "网关错误",
        503: "服务暂时不可用"
    }
    
    message = message_map.get(exc.status_code, str(exc.detail))
    if isinstance(exc.detail, str):
        message = exc.detail
    
    logger.warning(f"HTTP异常: {exc.status_code} - {message} | 路径: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": message,
            "success": False
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    error_id = id(exc)
    logger.error(f"未捕获异常 [{error_id}]: {type(exc).__name__}: {str(exc)}")
    logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
    
    # 在调试模式下返回详细错误信息
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "success": False,
                "detail": {
                    "error_id": error_id,
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc().split("\n")
                }
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误，请稍后重试",
            "success": False,
            "detail": {"error_id": error_id}
        }
    )


# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["健康检查"])
async def root():
    """
    根路径健康检查
    
    Returns:
        dict: 应用基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "status": "running"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """
    健康检查接口
    
    Returns:
        dict: 健康状态
    """
    from app.core.cache import cache_manager
    from app.core.websocket import ws_manager
    
    return {
        "status": "healthy",
        "database": "connected",
        "cache": cache_manager.get_stats(),
        "websocket": ws_manager.get_stats(),
        "realtime": realtime_service.get_stats()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
