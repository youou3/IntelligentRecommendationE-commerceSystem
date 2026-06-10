# MCP 与 SKILL 设计说明

## 1. 文档目的

本文档用于统一 MCP 调度中心和 SKILL 能力模块的设计方式，确保能力注册、调用、降级、日志和版本管理有一致规则。相关接口、工作流和数据模型约束见 [api.md](api.md)、[workflow_design.md](workflow_design.md) 和 [database.md](database.md)。

## 2. MCP 调度中心职责

- 统一注册 SKILL。
- 根据业务场景选择并调用 SKILL。
- 管理 SKILL 输入输出协议。
- 记录调用日志、耗时和异常。
- 为 WORKFLOW 提供统一能力入口。

## 3. SKILL 设计原则

- 一个 SKILL 只处理一类业务能力。
- SKILL 必须可独立调用。
- SKILL 必须定义清晰输入输出。
- SKILL 不直接承担流程编排职责。
- SKILL 调用必须可追踪、可监控、可回放。

## 4. 标准 SKILL 协议

建议所有 SKILL 统一遵循如下结构：

```python
class BaseSkill:
    name = ""
    version = "1.0.0"

    def validate(self, payload: dict) -> bool:
        raise NotImplementedError

    def execute(self, payload: dict) -> dict:
        raise NotImplementedError
```

标准返回建议如下：

```json
{
  "success": true,
  "code": "OK",
  "message": "success",
  "data": {}
}
```

## 5. 首批 SKILL 划分

### 5.1 行为采集 SKILL

- 负责行为标准化。
- 负责行为事件结构化。
- 负责事件写入前的基础校验。

### 5.2 用户画像 SKILL

- 负责用户标签聚合。
- 负责画像更新。
- 负责阶段识别与偏好计算。

### 5.3 推荐 SKILL

- 负责候选集生成。
- 负责相似度计算。
- 负责推荐过滤与排序。
- 负责推荐解释输出。

### 5.4 选品 SKILL

- 负责商品评分。
- 负责商品分层。
- 负责输出运营建议。

### 5.5 库存预警 SKILL

- 负责库存风险识别。
- 负责预警等级判断。
- 负责输出预警原因。

### 5.6 补货建议 SKILL

- 负责补货量计算。
- 负责风险说明输出。
- 负责给出清仓或观察建议。

## 6. 调用日志要求

每次调用都应记录：

- `tenant_id`
- `merchant_id`
- `skill_name`
- `skill_version`
- `request_id`
- `input_payload`
- `output_payload`
- `status`
- `cost_ms`
- `error_message`
- `created_at`

## 7. 异常与降级

- SKILL 调用失败时应有明确错误码。
- MCP 可按场景选择降级策略。
- 推荐类能力可降级到热门商品或规则推荐。
- 库存类能力可降级到最近一次稳定结果或人工审批。
- 降级必须写入日志，便于复盘。

## 8. 版本管理

- SKILL 必须带版本号。
- 新版本上线应保留旧版本一段时间，避免调用方同时切换。
- MCP 应支持按能力名和版本号路由。
- 版本升级时需要检查输入输出兼容性。

## 9. 与 WORKFLOW 的关系

- WORKFLOW 负责编排流程。
- MCP 负责调用单个 SKILL。
- SKILL 只做能力本身。
- WORKFLOW 不应直接嵌入复杂业务算法。

## 10. 备注

后续如果能力数量继续增长，可以继续补充：

- SKILL 插件市场设计。
- SKILL 权限控制设计。
- SKILL 沙箱与隔离设计。

## 11. 第四阶段落地说明

当前第四阶段已落地最小可用 MCP 调度层：

- `app/core/mcp.py`：提供 `SkillRegistry`、`MCPDispatcher`、统一标准响应和调用日志写入。
- `app/skills/registry.py`：集中注册默认 SKILL，包括行为采集、用户画像、推荐、选品、库存预警和补货建议。
- `GET /api/mcp/skills`：查询已注册 SKILL。
- `GET /api/mcp/skill-call-logs`：按租户、商家、能力和状态查询最近调用日志。

### 11.1 标准响应

MCP 调用返回统一结构：

```json
{
  "success": true,
  "code": "OK",
  "message": "success",
  "request_id": "REQ10001",
  "data": {},
  "fallback_used": false
}
```

### 11.2 调用日志

每次通过 MCP 调用 SKILL 时写入 MongoDB `skill_call_logs`：

- `tenant_id`
- `merchant_id`
- `skill_name`
- `skill_version`
- `request_id`
- `input_payload`
- `output_payload`
- `status`
- `cost_ms`
- `error_message`
- `fallback_used`
- `created_at`

MongoDB 不可用时不阻断业务主流程。

### 11.3 已改造能力

以下服务已通过 MCP 调用 SKILL：

- `RecommendationService` -> `recommendation`
- `ProductSelectionService` -> `product_selection`
- `InventoryService.run_warning_workflow` -> `inventory_warning`
- `InventoryService.suggest_replenishment` -> `replenishment`

保留直接调用 SKILL 的单元测试能力，便于算法逻辑独立验证。

### 11.4 降级策略

当前已配置基础降级：

- 推荐、选品、库存预警：降级为空结果列表，由业务服务继续执行已有兜底逻辑。
- 补货建议：降级为 `manual_review`，建议补货量为 `0`，并返回风险说明。

后续可继续把降级策略拆成按租户、商家、场景可配置的策略表。
