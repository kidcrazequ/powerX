# PowerX 智能电力交易系统

<div align="center">
  <img src="https://img.shields.io/badge/PowerX-v1.0.0-blue?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react" alt="React" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License" />
</div>

<div align="center">
  <h3>⚡ AI 赋能的中国电力市场交易平台</h3>
  <p>基于 DeepSeek 大模型，为各水平交易员提供智能辅助决策</p>
</div>

---

## Overview

PowerX 是一个专为中国电力市场设计的 **智能交易系统**，集成了先进的 AI 能力，帮助电力交易员做出更好的交易决策。无论是新手还是资深交易员，都能通过 PowerX 获得专业级的市场分析和策略建议。

PowerX is an **intelligent trading system** designed specifically for China's electricity market, integrating advanced AI capabilities to help power traders make better trading decisions.

---

## Features

* **🔮 电价预测** - 基于历史数据和市场因素，预测各省24小时电价走势
* **💡 策略推荐** - 根据风险偏好和市场状态，自动生成交易策略
* **📚 政策解读** - RAG 知识库支持，智能解答电力市场政策问题
* **📊 风险评估** - 实时监控持仓风险，及时预警
* **📝 报告生成** - AI 自动生成日报、周报、月报
* **🔐 安全合规** - 双因子认证、数据脱敏、IP 白名单、数字签名
* **📈 算法交易** - TWAP/VWAP 策略、条件单、组合订单
* **🌐 跨省交易** - 支持跨省电力交易管理
* **📱 移动端适配** - PWA 支持，随时随地交易

---

## Supported Provinces

| 省份 | 现货市场 | 价格机制 | 特点 |
|------|---------|---------|------|
| 广东 | ✅ 运行 | 节点电价 | 15分钟结算 |
| 浙江 | ✅ 运行 | 统一出清 | 高频交易 |
| 山东 | ✅ 运行 | 统一出清 | 允许负电价 |
| 山西 | ✅ 运行 | 统一出清 | 煤电为主 |
| 甘肃 | ✅ 运行 | 统一出清 | 新能源外送 |

---

## Tech Stack

### Backend
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 主语言 |
| FastAPI | 0.100+ | Web 框架 |
| PostgreSQL | 15+ | 主数据库 |
| TimescaleDB | - | 时序数据 |
| Redis | 7+ | 缓存/消息 |
| DeepSeek API | - | AI 大模型 |
| LangChain | - | AI 编排 |
| Celery | - | 异步任务 |

### Frontend
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18 | UI 框架 |
| TypeScript | 5+ | 类型安全 |
| Ant Design | 5 | UI 组件库 |
| ECharts | 5 | 数据可视化 |
| Zustand | - | 状态管理 |
| Vite | 5+ | 构建工具 |

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/kidcrazequ/powerX.git
cd powerX

# Start all services
cd docker
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Installation

#### Backend Setup

```bash
# Enter backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env file with your configuration

# Start server
uvicorn main:app --reload --port 8000
```

#### Frontend Setup

```bash
# Enter frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Usage

### Quick Start

1. **启动服务** - 使用 Docker 或手动启动后端和前端服务
2. **访问系统** - 打开浏览器访问 http://localhost:3000
3. **登录账户** - 使用测试账号或注册新账号
4. **开始交易** - 查看市场行情，使用 AI 功能辅助决策

### Example Workflows

```
查看广东省实时电价走势

分析今日市场异常波动原因

生成本周交易报告

使用 TWAP 策略执行大单交易

设置价格预警条件单
```

### How It Works

1. **数据采集** - 实时获取各省电力交易中心市场数据
2. **AI 分析** - DeepSeek 大模型分析市场趋势和交易机会
3. **策略生成** - 根据用户风险偏好生成个性化交易策略
4. **风险管理** - 实时监控持仓风险，自动预警和止损
5. **报告输出** - 自动生成交易报告和市场分析

---

## Project Structure

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
├── docker/                      # Docker 配置
│
└── k8s/                         # Kubernetes 配置
```

---

## API Documentation

启动后端后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main API Endpoints

| 模块 | 端点 | 描述 |
|------|------|------|
| 认证 | `/api/v1/auth/*` | 用户登录、注册、刷新令牌 |
| 交易 | `/api/v1/trading/*` | 订单管理、持仓查询 |
| 市场 | `/api/v1/market/*` | 市场数据、价格查询 |
| 合同 | `/api/v1/contracts/*` | 合同管理、分解计划 |
| 结算 | `/api/v1/settlement/*` | 结算记录、费用分析 |
| AI | `/api/v1/ai/*` | 智能问答、价格预测、策略推荐 |
| 报告 | `/api/v1/reports/*` | 报告生成、模板管理 |
| 算法交易 | `/api/v1/algo-trading/*` | TWAP/VWAP 策略 |
| 条件单 | `/api/v1/conditional-orders/*` | 条件触发订单 |
| 组合订单 | `/api/v1/combo-orders/*` | 多腿订单管理 |

---

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/powerx

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# DeepSeek API
DEEPSEEK_API_KEY=your-deepseek-api-key

# Application
DEBUG=true
DEFAULT_PROVINCE=广东
```

---

## Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test
```

---

## Changelog

### v1.0.0 (2026-01-08)
- ✅ 初始版本发布
- ✅ 支持广东、浙江、山东、山西、甘肃省份
- ✅ 集成 DeepSeek AI 能力
- ✅ 完整的现货和中长期交易功能
- ✅ AI 驱动的电价预测和策略推荐
- ✅ 算法交易（TWAP/VWAP）支持
- ✅ 条件单和组合订单管理
- ✅ 双因子认证和安全增强
- ✅ 数据大屏和预测对账功能
- ✅ 跨省交易和期权交易支持

---

## Roadmap

- [ ] 更多省份现货市场接入
- [ ] 移动端 App 开发
- [ ] 更多 AI 模型支持
- [ ] 量化回测系统
- [ ] 社区交易策略分享

---

## Contributing

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## License

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## About

PowerX 是一个 **AI 驱动的电力交易智能系统**，专为中国电力市场设计。

### Topics

`power-trading` `electricity-market` `ai-trading` `deepseek` `fastapi` `react` `china-market` `smart-grid` `energy-trading` `algorithmic-trading`

---

<div align="center">
  <p>Made with ⚡ by <strong>PowerX Team</strong></p>
  <p>
    <a href="https://github.com/kidcrazequ/powerX">GitHub</a> •
    <a href="https://github.com/kidcrazequ/powerX/issues">Issues</a> •
    <a href="https://github.com/kidcrazequ/powerX/pulls">Pull Requests</a>
  </p>
</div>
