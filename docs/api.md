# API 设计说明

## 1. 文档目的

本文档用于统一系统接口设计规范，覆盖鉴权、幂等、分页、错误码、日志追踪与租户隔离等基础约束。相关架构与数据约束见 [architecture.md](architecture.md)、[database.md](database.md) 和 [开发文档_架构接口与多租户预留.md](开发文档_架构接口与多租户预留.md)。

## 2. 通用接口约束

### 2.1 通用入参字段

建议所有接口按场景统一携带以下字段：

- `tenant_id`
- `merchant_id`
- `request_id`
- `scene`
- `user_id`
- `product_id`
- `event_id`

### 2.2 通用返回结构

建议统一返回格式：

```json
{
  "success": true,
  "code": "OK",
  "message": "success",
  "request_id": "REQ10001",
  "data": {}
}
```

### 2.3 接口设计要求

- 所有写接口必须具备幂等能力，至少支持 `event_id` 或业务唯一键。
- 所有上报接口必须支持追踪 ID。
- 所有列表接口必须支持分页。
- 所有查询接口必须默认按租户隔离。
- 所有推荐类接口必须支持场景参数。
- 所有库存和补货接口必须返回状态机字段，方便前端展示流转过程。

### 2.4 接口文档建议补齐项

每个接口文档建议补齐以下内容：

- 接口名称。
- 请求方法。
- 路径。
- 鉴权方式。
- 请求参数。
- 响应参数。
- 错误码。
- 幂等规则。
- 限流规则。
- 日志字段。
- 示例请求与响应。

## 3. 核心接口清单

### 3.1 行为采集接口

`POST /api/behavior/collect`

用途：采集用户行为并写入事件流。

建议参数：

- `tenant_id`
- `merchant_id`
- `request_id`
- `event_id`
- `user_id`
- `event_type`
- `product_id`
- `category_id`
- `tags`
- `source`
- `duration`
- `scene`

### 3.2 推荐接口

`GET /api/recommendations`

用途：根据用户画像和场景输出推荐结果。

建议参数：

- `tenant_id`
- `merchant_id`
- `request_id`
- `user_id`
- `scene`
- `limit`
- `exclude_product_ids`
- `min_stock`
- `dedup_days`
- `max_recent_exposures`

返回结果建议包含：

- 推荐商品列表。
- 推荐请求 ID。
- 推荐策略标识。
- 冷启动标识。
- 推荐解释字段。
- 商品库存信息。

### 3.3 选品评分接口

`POST /api/products/selection-score`

用途：输出商品选品评分、商品分层和运营建议。

建议参数：

- `tenant_id`
- `merchant_id`
- `request_id`
- `product_ids`
- `date_range`
- `persist`

返回结果建议包含：

- 商品选品评分。
- 商品分层。
- 运营建议。
- 关键指标：曝光、点击、加购、转化、CTR、加购率、转化率、毛利、有效库存。

### 3.4 库存预警接口

`GET /api/inventory/warnings`

用途：查询库存预警列表。

建议参数：

- `tenant_id`
- `merchant_id`
- `request_id`
- `warning_level`
- `category_id`
- `status`

### 3.5 补货建议接口

`POST /api/inventory/replenishment/suggest`

用途：生成补货建议和风险说明。

建议参数：

- `tenant_id`
- `merchant_id`
- `request_id`
- `product_id`
- `forecast_days`

### 3.6 BI 看板接口

`GET /api/dashboard/overview`

用途：输出总览 KPI，辅助第一、二阶段测试和后续运营观察。

`GET /api/dashboard/recommendation-funnel`

用途：输出推荐漏斗、趋势和场景表现。

`GET /api/dashboard/product-selection`

用途：输出商品分层、选品得分和风险商品。

`GET /api/dashboard/user-profiles`

用途：输出用户画像分布和偏好分布。

`GET /api/dashboard/inventory-health`

用途：输出库存健康、低库存和缺货风险。

建议通用参数：

- `tenant_id`
- `merchant_id`
- `request_id`
- `start_date`
- `end_date`
- `scene`
- `category_id`
- `limit`

## 4. 接口实现优先级

### 第一优先级

- 行为采集接口。
- 推荐接口。
- 库存预警接口。
- 补货建议接口。

### 第二优先级

- 选品评分接口。
- 推荐曝光回流接口。
- 审批流相关接口。
- 工作流查询接口。

## 5. 备注

后续若补充完整 OpenAPI / Swagger 文档，可直接以本文件作为字段与约束基线。
