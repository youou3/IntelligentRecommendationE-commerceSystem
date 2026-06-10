# IntelligentRecommendationE-commerceSystem

中小型智能电商 SaaS 系统的阶段性实现，围绕“行为采集 -> 用户画像 -> 推荐 -> 选品 -> 库存预警 -> 自动补货 -> MCP 标准化 -> 运营复盘看板”形成可验证闭环。

## 已实现能力

### 第一阶段：数据与基础闭环

- Flask 项目基础结构。
- MySQL + MongoDB 基础连接。
- 用户、商品、订单、库存、用户画像、推荐反馈核心模型。
- 用户行为采集接口。
- 基础用户画像生成接口。
- 标签匹配推荐接口。
- 推荐曝光 / 点击 / 加购 / 转化反馈记录。
- `init_db.py` MySQL 初始化脚本。

### 第二阶段：推荐与选品增强

- 商品标签向量化。
- 用户画像权重升级与时间衰减。
- 余弦相似度推荐。
- 库存、状态、去重、频控等业务过滤。
- 新用户 / 新商品冷启动兜底。
- 智能选品评分接口。
- 商品分层与运营建议输出。

### 第三阶段：库存与补货工作流

- 库存预警 SKILL。
- 补货建议 SKILL。
- 库存预警 WORKFLOW。
- 自动补货 WORKFLOW。
- 补货单生成与状态记录。
- 库存预警列表接口。
- 库存变更事件处理，支持 `event_id` 幂等。

### 第四阶段：MCP / SKILL 标准化

- MCP 注册中心：`SkillRegistry`。
- MCP 调度器：`MCPDispatcher`。
- 统一 SKILL 标准响应。
- SKILL 调用日志、耗时和异常记录。
- 基础异常降级机制。
- 推荐、选品、库存预警、补货建议已通过 MCP 调用。
- MCP 查询接口：
  - `GET /api/mcp/skills`
  - `GET /api/mcp/skill-call-logs`

### 第五阶段：运营复盘与数据看板

- 推荐效果看板。
- 用户画像分布看板。
- 商品选品看板。
- 库存风险看板。
- 补货效果复盘。
- 运营复盘总览。
- MCP 调用健康与工作流健康指标。
- 商家维度数据隔离，核心查询均按 `tenant_id + merchant_id` 过滤。

### BI 看板

- 前后端分离的 Vue 3 + Vite + ECharts 看板。
- 左侧按钮多页面展示：总览、推荐、选品、画像、库存、预警、补货、工作流。
- 支持演示模式，无需本地数据库也能查看。
- 真实模式通过 Vite 代理访问后端 `/api`。
- 配色保持深蓝、青绿、霓虹高亮的大屏控制台风格。
- 详细设计见 [docs/bi_dashboard.md](docs/bi_dashboard.md)。

## 1. 本地启动

### 1.1 安装后端依赖

```bash
python3 -m pip install -r requirements.txt
```

### 1.2 配置环境变量

复制 `.env.example` 并按需修改：

```bash
cp .env.example .env
```

关键配置：

- `SECRET_KEY`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `MONGO_URI`
- `MONGO_DB_NAME`

### 1.3 初始化 MySQL 表

```bash
python init_db.py
```

如果 MySQL 连接正常、账号具备建表权限，这会在 `intelligent_recommendation` 库里创建当前模型对应的表。脚本会自动加载 `.env`。若执行时报 `Can't connect to MySQL server`，先检查 `.env` 里的 `MYSQL_HOST`、`MYSQL_PORT` 和数据库服务是否可达。

### 1.4 生成测试种子数据

```bash
python seed_data.py
```

该脚本会创建一批可用于看板和推荐 / 选品 / 库存测试的示例数据，包括商品、库存、画像、反馈和 Mongo 行为日志。

### 1.5 启动后端服务

```bash
python run.py
```

默认监听 `http://127.0.0.1:5000`。

### 1.6 启动 BI 前端

```bash
cd web
npm install
npm run dev
```

默认监听 `http://localhost:5173`，并通过 Vite 代理访问后端 `/api`。

### 1.7 构建前端

```bash
cd web
npm run build
```

## 2. 运行测试

```bash
python3 -m pytest
```

当前测试覆盖：

- 行为采集接口。
- 用户画像生成接口。
- 推荐接口。
- 推荐反馈接口。
- 行为与反馈幂等性。
- 第二阶段推荐算法。
- 第二阶段选品评分。
- 第三阶段库存预警、补货建议、库存事件幂等。
- 第四阶段 MCP 注册、标准响应和调用日志。
- 第五阶段补货复盘、运营复盘和商家维度隔离。

## 3. 主要接口

### 健康检查

- `GET /health`

### 行为采集

- `POST /api/behavior/collect`

### 用户画像

- `POST /api/user-profiles/generate`

### 推荐

- `GET /api/recommendations`
- `POST /api/recommendations/feedback`

### 选品

- `POST /api/products/selection-score`

### 库存与补货

- `GET /api/inventory/warnings`
- `POST /api/inventory/warnings/run`
- `POST /api/inventory/replenishment/suggest`
- `POST /api/inventory/events`

### MCP

- `GET /api/mcp/skills`
- `GET /api/mcp/skill-call-logs`

### BI / 运营看板

- `GET /api/dashboard/overview`
- `GET /api/dashboard/recommendation-funnel`
- `GET /api/dashboard/product-selection`
- `GET /api/dashboard/user-profiles`
- `GET /api/dashboard/inventory-health`
- `GET /api/dashboard/replenishment-review`
- `GET /api/dashboard/operations-review`

## 4. 项目结构

```text
app/
  api/        Flask API 蓝图
  core/       配置、数据库、响应、校验、MCP 调度
  models/     SQLAlchemy 模型
  services/   业务服务与 WORKFLOW 编排
  skills/     可独立调用的 SKILL 能力
docs/         设计与阶段文档
tests/        pytest 测试
web/          Vue 3 + Vite BI 看板
```

## 5. 项目文档

- [docs/README.md](docs/README.md)：文档索引。
- [docs/开发文档_迭代功能.md](docs/开发文档_迭代功能.md)：五阶段迭代规划与当前落地状态。
- [docs/开发文档_架构接口与多租户预留.md](docs/开发文档_架构接口与多租户预留.md)：架构、接口和多租户预留说明。
- [docs/api.md](docs/api.md)：接口统一约束与核心接口清单。
- [docs/database.md](docs/database.md)：MySQL / MongoDB 数据模型设计。
- [docs/architecture.md](docs/architecture.md)：系统分层、MCP / SKILL / WORKFLOW 职责。
- [docs/workflow_design.md](docs/workflow_design.md)：库存预警和自动补货工作流。
- [docs/mcp_skill_design.md](docs/mcp_skill_design.md)：MCP 注册、SKILL 协议、调用日志与降级。
- [docs/bi_dashboard.md](docs/bi_dashboard.md)：BI 看板与第五阶段运营复盘设计。
- [docs/phase3_dashboard_plan.md](docs/phase3_dashboard_plan.md)：第三阶段看板接入与左侧多页面改造规划。

## 6. 说明

本仓库当前已完成从推荐闭环到运营复盘看板的阶段性最小可用实现。后续可继续扩展权限体系、审批流、A/B 测试、报表导出、定时任务调度和更完整的多租户 SaaS 管理能力。
