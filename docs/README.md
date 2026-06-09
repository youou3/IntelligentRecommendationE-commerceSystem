# 文档索引

## 1. 总览

本目录用于存放中小型智能电商 SaaS 系统的设计与开发文档。建议先看索引，再按需要进入对应文档。

## 2. 文档清单

### 2.1 主规划文档

- [开发文档_迭代功能.md](开发文档_迭代功能.md)：按阶段组织的迭代开发规划，包含里程碑、测试、风险和 MVP 范围。建议先读这份，再进入专项文档。
- [开发文档_架构接口与多租户预留.md](开发文档_架构接口与多租户预留.md)：补充多租户预留字段、架构边界、接口与数据模型约束，适合作为主规划的配套说明。

### 2.2 专项设计文档

- [architecture.md](architecture.md)：系统分层、模块边界、MCP / SKILL / WORKFLOW 职责说明。
- [api.md](api.md)：接口统一约束、核心接口清单、幂等和追踪要求。
- [database.md](database.md)：MySQL / MongoDB 表与集合设计、字段、索引和租户预留要求。
- [workflow_design.md](workflow_design.md)：库存预警、自动补货等工作流设计与状态机约束。
- [mcp_skill_design.md](mcp_skill_design.md)：MCP 注册中心、SKILL 协议、调用日志和降级规则。
- [bi_dashboard.md](bi_dashboard.md)：前后端分离 BI 看板设计，覆盖第一、二阶段测试与运营观察。

## 3. 使用建议

- 先读 `开发文档_迭代功能.md`，理解整体阶段和交付顺序。
- 再按需要进入 `architecture.md`、`api.md`、`database.md` 等专项文档。
- 如果要补充新能力，优先更新专项文档，再回写主规划文档中的对应阶段。

## 4. 后续扩展建议

若项目继续扩展，建议在本目录继续补充：

- `security.md`
- `observability.md`
- `deployment.md`
- `openapi.md`
