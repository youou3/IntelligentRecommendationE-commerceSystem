# IntelligentRecommendationE-commerceSystem

中小型智能电商 SaaS 系统的阶段性实现。

## 已实现能力

### 第一阶段

- Flask 项目基础结构
- MySQL + MongoDB 基础连接
- 用户、商品、订单、库存、用户画像、推荐反馈核心模型
- 用户行为采集接口
- 基础用户画像生成接口
- 标签匹配推荐接口
- 推荐曝光 / 点击 / 加购 / 转化反馈记录
- `init_db.py` MySQL 初始化脚本

### 第二阶段

- 商品标签向量化
- 用户画像权重升级与时间衰减
- 余弦相似度推荐
- 业务过滤与冷启动推荐
- 智能选品评分接口
- 商品分层与运营建议

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

### 1.3 初始化 MySQL 表

```bash
python init_db.py
```

如果 MySQL 连接正常、账号具备建表权限，这会在 `intelligent_recommendation` 库里创建当前模型对应的表。脚本会自动加载 `.env`。若执行时报 `Can't connect to MySQL server`，先检查 `.env` 里的 `MYSQL_HOST`、`MYSQL_PORT` 和数据库服务是否可达。

### 1.4 启动服务

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
- 第二阶段推荐算法
- 第二阶段选品评分

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

### 选品评分

- `POST /api/products/selection-score`

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

本仓库当前优先实现推荐闭环的最小可用版本，并逐步补齐选品、库存预警、自动补货和工作流编排能力。
