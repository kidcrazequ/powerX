"""
PowerX AI 配置管理
创建日期: 2026-01-07
作者: zhi.qu

支持多模型版本、A/B测试
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import random
from loguru import logger


class ModelVersion(str, Enum):
    """模型版本"""
    DEEPSEEK_V2 = "deepseek-v2"
    DEEPSEEK_V3 = "deepseek-v3"
    DEEPSEEK_CODER = "deepseek-coder"
    DEEPSEEK_CHAT = "deepseek-chat"


class ModelCapability(str, Enum):
    """模型能力"""
    PRICE_PREDICTION = "price_prediction"
    STRATEGY_GENERATION = "strategy_generation"
    RISK_ANALYSIS = "risk_analysis"
    QA = "qa"
    REPORT_GENERATION = "report_generation"
    ANOMALY_DETECTION = "anomaly_detection"


@dataclass
class ModelConfig:
    """模型配置"""
    version: ModelVersion
    base_url: str
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    capabilities: List[ModelCapability] = field(default_factory=list)
    
    # A/B测试权重
    weight: float = 1.0
    
    # 性能指标
    avg_latency_ms: float = 0
    success_rate: float = 1.0
    total_requests: int = 0


@dataclass
class ABTestGroup:
    """A/B测试组"""
    name: str
    models: List[ModelConfig]
    
    def select_model(self) -> ModelConfig:
        """根据权重选择模型"""
        total_weight = sum(m.weight for m in self.models)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for model in self.models:
            cumulative += model.weight
            if r <= cumulative:
                return model
        
        return self.models[-1]


class AIConfigManager:
    """AI配置管理器"""
    
    def __init__(self):
        self._models: Dict[str, ModelConfig] = {}
        self._ab_tests: Dict[str, ABTestGroup] = {}
        self._default_model: Optional[str] = None
        self._capability_mapping: Dict[ModelCapability, str] = {}
    
    def register_model(self, name: str, config: ModelConfig):
        """注册模型"""
        self._models[name] = config
        
        # 注册能力映射
        for capability in config.capabilities:
            if capability not in self._capability_mapping:
                self._capability_mapping[capability] = name
        
        if self._default_model is None:
            self._default_model = name
        
        logger.info(f"注册AI模型: {name} ({config.version.value})")
    
    def get_model(self, name: str = None) -> Optional[ModelConfig]:
        """获取模型配置"""
        if name is None:
            name = self._default_model
        return self._models.get(name)
    
    def get_model_for_capability(self, capability: ModelCapability) -> Optional[ModelConfig]:
        """根据能力获取最佳模型"""
        model_name = self._capability_mapping.get(capability, self._default_model)
        return self._models.get(model_name)
    
    def create_ab_test(self, name: str, model_names: List[str], weights: List[float] = None):
        """创建A/B测试"""
        models = [self._models[n] for n in model_names if n in self._models]
        
        if weights:
            for model, weight in zip(models, weights):
                model.weight = weight
        
        self._ab_tests[name] = ABTestGroup(name=name, models=models)
        logger.info(f"创建A/B测试: {name}, 包含 {len(models)} 个模型")
    
    def get_ab_test_model(self, test_name: str) -> Optional[ModelConfig]:
        """从A/B测试中选择模型"""
        ab_test = self._ab_tests.get(test_name)
        if ab_test:
            return ab_test.select_model()
        return None
    
    def update_model_stats(self, name: str, latency_ms: float, success: bool):
        """更新模型统计"""
        model = self._models.get(name)
        if not model:
            return
        
        model.total_requests += 1
        
        # 更新平均延迟 (指数移动平均)
        alpha = 0.1
        model.avg_latency_ms = alpha * latency_ms + (1 - alpha) * model.avg_latency_ms
        
        # 更新成功率
        if success:
            model.success_rate = 0.99 * model.success_rate + 0.01
        else:
            model.success_rate = 0.99 * model.success_rate
    
    def get_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模型统计"""
        return {
            name: {
                "version": model.version.value,
                "avg_latency_ms": round(model.avg_latency_ms, 2),
                "success_rate": round(model.success_rate, 4),
                "total_requests": model.total_requests
            }
            for name, model in self._models.items()
        }
    
    def set_default_model(self, name: str):
        """设置默认模型"""
        if name in self._models:
            self._default_model = name
            logger.info(f"设置默认AI模型: {name}")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """列出所有模型"""
        return [
            {
                "name": name,
                "version": model.version.value,
                "capabilities": [c.value for c in model.capabilities],
                "is_default": name == self._default_model
            }
            for name, model in self._models.items()
        ]


# 单例
ai_config = AIConfigManager()


def init_ai_models(deepseek_api_key: str = None, deepseek_base_url: str = None):
    """初始化AI模型配置"""
    api_key = deepseek_api_key or "demo-key"
    base_url = deepseek_base_url or "https://api.deepseek.com/v1"
    
    # 注册 DeepSeek V3 (最新版本)
    ai_config.register_model("deepseek_v3", ModelConfig(
        version=ModelVersion.DEEPSEEK_V3,
        base_url=base_url,
        api_key=api_key,
        max_tokens=8192,
        temperature=0.7,
        capabilities=[
            ModelCapability.PRICE_PREDICTION,
            ModelCapability.STRATEGY_GENERATION,
            ModelCapability.RISK_ANALYSIS,
            ModelCapability.ANOMALY_DETECTION
        ]
    ))
    
    # 注册 DeepSeek Chat (对话优化)
    ai_config.register_model("deepseek_chat", ModelConfig(
        version=ModelVersion.DEEPSEEK_CHAT,
        base_url=base_url,
        api_key=api_key,
        max_tokens=4096,
        temperature=0.8,
        capabilities=[
            ModelCapability.QA,
            ModelCapability.REPORT_GENERATION
        ]
    ))
    
    # 设置默认模型
    ai_config.set_default_model("deepseek_v3")
    
    # 创建A/B测试 (预测模型对比)
    ai_config.create_ab_test(
        "prediction_test",
        ["deepseek_v3", "deepseek_chat"],
        [0.8, 0.2]  # 80% 使用 v3, 20% 使用 chat
    )
    
    logger.info("AI模型配置初始化完成")


def get_ai_config() -> AIConfigManager:
    """获取AI配置管理器"""
    return ai_config
