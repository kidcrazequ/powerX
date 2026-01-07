# PowerX 智能电力交易系统

<div align="center">
  <h3>⚡ AI 赋能的中国电力市场交易平台</h3>
  <p>基于 DeepSeek 大模型，为各水平交易员提供智能辅助决策</p>
</div>

---

## 📋 项目概述

PowerX 是一个专为中国电力市场设计的智能交易系统，集成了先进的 AI 能力，帮助电力交易员做出更好的交易决策。无论是新手还是资深交易员，都能通过 PowerX 获得专业级的市场分析和策略建议。

### ✨ 核心特性

- 🔮 **电价预测** - 基于历史数据和市场因素，预测各省24小时电价走势
- 💡 **策略推荐** - 根据风险偏好和市场状态，自动生成交易策略
- 📚 **政策解读** - RAG 知识库支持，智能解答电力市场政策问题
- 📊 **风险评估** - 实时监控持仓风险，及时预警
- 📝 **报告生成** - AI 自动生成日报、周报、月报

### 🌏 支持省份

| 省份 | 现货市场 | 价格机制 | 特点 |
|------|---------|---------|------|
| 广东 | ✅ 运行 | 节点电价 | 15分钟结算 |
| 浙江 | ✅ 运行 | 统一出清 | 高频交易 |
| 山东 | ✅ 运行 | 统一出清 | 允许负电价 |
| 山西 | ✅ 运行 | 统一出清 | 煤电为主 |
| 甘肃 | ✅ 运行 | 统一出清 | 新能源外送 |

---

## 🛠 技术栈

### 后端
- **框架**: Python 3.11 + FastAPI
- **数据库**: PostgreSQL + TimescaleDB
- **缓存**: Redis
- **AI**: DeepSeek API + LangChain
- **异步**: Celery

### 前端
- **框架**: React 18 + TypeScript
- **UI**: Ant Design Pro 5
- **图表**: ECharts
- **状态管理**: Zustand
- **构建**: Vite

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### 后端安装

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入配置

# 启动服务
uvicorn main:app --reload --port 8000
```

### 前端安装

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Docker 部署

```bash
# 进入 docker 目录
cd docker

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 📁 项目结构

```
PowerX/
├── backend/                      # 后端服务
│   ├── app/
│   │   ├── api/v1/              # API 端点
│   │   ├── core/                # 核心配置
│   │   ├── models/              # 数据模型
│   │   ├── services/            # 业务服务
│   │   ├── ai/                  # AI 模块
│   │   └── china_market/        # 中国市场规则
│   ├── tests/                   # 测试文件
│   └── main.py                  # 入口文件
│
├── frontend/                    # 前端应用
│   ├── src/
│   │   ├── pages/              # 页面组件
│   │   ├── components/         # 通用组件
│   │   ├── stores/             # 状态管理
│   │   └── services/           # API 调用
│   └── package.json
│
├── data/                        # 数据文件
│   ├── mock/                   # 模拟数据
│   └── knowledge_base/         # 知识库
│
└── docker/                      # Docker 配置
```

---

## 🔌 API 文档

启动后端后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要 API 端点

| 模块 | 端点 | 描述 |
|------|------|------|
| 认证 | `/api/v1/auth/*` | 用户登录、注册、刷新令牌 |
| 交易 | `/api/v1/trading/*` | 订单管理、持仓查询 |
| 市场 | `/api/v1/market/*` | 市场数据、价格查询 |
| 合同 | `/api/v1/contracts/*` | 合同管理、分解计划 |
| 结算 | `/api/v1/settlement/*` | 结算记录、费用分析 |
| AI | `/api/v1/ai/*` | 智能问答、价格预测、策略推荐 |
| 报告 | `/api/v1/reports/*` | 报告生成、模板管理 |

---

## ⚙️ 配置说明

### 环境变量

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/powerx

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# DeepSeek API
DEEPSEEK_API_KEY=your-deepseek-api-key

# 应用
DEBUG=true
DEFAULT_PROVINCE=广东
```

---

## 🧪 测试

```bash
# 运行后端测试
cd backend
pytest

# 运行前端测试
cd frontend
npm test
```

---

## 📝 更新日志

### v1.0.0 (2026-01-07)
- ✅ 初始版本发布
- ✅ 支持广东、浙江、山东、山西、甘肃省份
- ✅ 集成 DeepSeek AI 能力
- ✅ 完整的现货和中长期交易功能
- ✅ AI 驱动的电价预测和策略推荐

---

## 📄 许可证

本项目仅供学习和演示用途。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

<div align="center">
  <p>Made with ⚡ by PowerX Team</p>
</div>
