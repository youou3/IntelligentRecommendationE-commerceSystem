# IntelligentRecommendationE-commerceSystem

中小型智能电商 SaaS 系统的第一阶段实现，包含：

- Flask 项目基础结构
- MySQL + MongoDB 基础连接
- 用户、商品、订单、库存、用户画像、推荐反馈核心模型
- 用户行为采集接口
- 基础用户画像生成接口
- 标签匹配推荐接口
- 推荐曝光 / 点击 / 加购 / 转化反馈记录

## 1. 本地启动

### 1.1 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

### 1.2 配置环境变量

复制 `.env.example` 并按需修改：

```bash
cp .env.example .env
```

### 1.3 启动服务

```bash
python run.py
```

默认监听 `http://127.0.0.1:5000`。

## 2. 运行测试

```bash
python3 -m pytest
```

当前测试覆盖：

- 行为采集接口
- 用户画像生成接口
- 推荐接口
- 推荐反馈接口
- 幂等性

## 3. 主要接口

### 健康检查

- `GET /health`

### 行为采集

- `POST /api/behavior/collect`

### 用户画像生成

- `POST /api/user-profiles/generate`

### 推荐

- `GET /api/recommendations`

### 推荐反馈

- `POST /api/recommendations/feedback`

## 4. 配置说明

`.env.example` 中包含以下关键配置：

- `SECRET_KEY`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `MONGO_URI`
- `MONGO_DB_NAME`

## 5. 项目文档

- [docs/README.md](docs/README.md)
- [docs/开发文档_迭代功能.md](docs/开发文档_迭代功能.md)
- [docs/api.md](docs/api.md)
- [docs/database.md](docs/database.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/workflow_design.md](docs/workflow_design.md)
- [docs/mcp_skill_design.md](docs/mcp_skill_design.md)

## 6. 说明

第一阶段只实现推荐闭环的最小可用版本，后续的选品、库存预警、自动补货和工作流编排会继续在现有结构上迭代。
