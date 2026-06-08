# 数据库设计说明

## 1. 文档目的

本文档用于统一 MySQL 与 MongoDB 的基础数据模型设计，重点说明核心表、集合、字段、索引和多租户预留要求。相关接口、架构和工作流约束见 [api.md](api.md)、[architecture.md](architecture.md) 和 [workflow_design.md](workflow_design.md)。

## 2. 多租户预留字段

所有核心业务表、事件集合建议统一预留以下字段：

- `tenant_id`：租户 ID。
- `merchant_id`：商家 ID。
- `org_id`：组织或门店 ID。
- `project_id`：项目空间 ID。
- `request_id`：请求追踪 ID。
- `event_id`：事件幂等 ID。
- `operator_id`：操作人 ID。

查询与写入都应默认带租户条件，避免跨租户数据泄漏。

## 3. MySQL 结构化表建议

### 3.1 `users`

建议字段：

- `id`
- `tenant_id`
- `merchant_id`
- `nickname`
- `channel`
- `member_level`
- `created_at`

### 3.2 `products`

建议字段：

- `id`
- `tenant_id`
- `merchant_id`
- `name`
- `category_id`
- `tags`
- `price`
- `cost_price`
- `gross_margin`
- `status`
- `created_at`

### 3.3 `orders`

建议字段：

- `id`
- `tenant_id`
- `merchant_id`
- `user_id`
- `order_status`
- `pay_status`
- `total_amount`
- `created_at`

### 3.4 `order_items`

建议字段：

- `id`
- `tenant_id`
- `merchant_id`
- `order_id`
- `product_id`
- `quantity`
- `price`
- `amount`

### 3.5 `user_profiles`

建议字段：

- `user_id`
- `tenant_id`
- `merchant_id`
- `tag_vector`
- `price_preference`
- `category_preference`
- `user_stage`
- `updated_at`

### 3.6 `inventory`

建议字段：

- `product_id`
- `tenant_id`
- `merchant_id`
- `available_stock`
- `locked_stock`
- `in_transit_stock`
- `safe_stock`
- `updated_at`

### 3.7 `inventory_logs`

建议字段：

- `id`
- `tenant_id`
- `merchant_id`
- `product_id`
- `change_type`
- `change_quantity`
- `request_id`
- `event_id`
- `created_at`

### 3.8 `replenishment_orders`

建议字段：

- `id`
- `tenant_id`
- `merchant_id`
- `product_id`
- `suggest_quantity`
- `approved_quantity`
- `status`
- `request_id`
- `created_at`

### 3.9 `approval_records`

建议字段：

- `id`
- `tenant_id`
- `merchant_id`
- `biz_type`
- `biz_id`
- `operator_id`
- `approval_status`
- `comment`
- `created_at`

### 3.10 `recommendation_feedback`

建议字段：

- `id`
- `tenant_id`
- `merchant_id`
- `request_id`
- `user_id`
- `product_id`
- `scene`
- `click_flag`
- `convert_flag`
- `created_at`

## 4. MongoDB 事件集合建议

### 4.1 `behavior_events`

建议包含：

- `tenant_id`
- `merchant_id`
- `event_id`
- `request_id`
- `event_type`
- `scene`
- `user_id`
- `product_id`
- `category_id`
- `source`
- `payload`
- `created_at`

### 4.2 `recommendation_logs`

建议包含：

- `tenant_id`
- `merchant_id`
- `request_id`
- `user_id`
- `scene`
- `recommended_products`
- `clicked_products`
- `converted_products`
- `created_at`

### 4.3 `inventory_warning_logs`

建议包含：

- `tenant_id`
- `merchant_id`
- `request_id`
- `product_id`
- `warning_level`
- `warning_reason`
- `status`
- `created_at`

### 4.4 `workflow_runs`

建议包含：

- `tenant_id`
- `merchant_id`
- `workflow_name`
- `run_id`
- `status`
- `input_payload`
- `output_payload`
- `created_at`

### 4.5 `skill_call_logs`

建议包含：

- `tenant_id`
- `merchant_id`
- `skill_name`
- `request_id`
- `input_payload`
- `output_payload`
- `status`
- `cost_ms`
- `created_at`

## 5. 状态类数据要求

对于库存、补货单、审批单等状态类对象，建议统一具备：

- 当前状态。
- 状态更新时间。
- 状态流转记录。
- 操作人信息。
- 关联事件 ID。

## 6. 索引建议

建议优先建立以下组合索引：

- `tenant_id + merchant_id`
- `tenant_id + user_id`
- `tenant_id + product_id`
- `tenant_id + request_id`
- `tenant_id + event_id`
- `tenant_id + created_at`

## 7. 备注

后续若补充 ER 图或正式建表 SQL，可直接以本文件作为字段与索引设计基线。
