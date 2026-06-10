# 第三阶段看板接入规划

## 1. 目标

将第三阶段已实现的库存预警、补货建议、库存事件和工作流运行记录接入现有 BI 看板。看板从当前单页总览扩展为左侧按钮导航的多页面控制台，同时保持现有深蓝、青绿、霓虹高亮的科技大屏配色风格不变。

## 2. 当前基础

### 2.1 已有后端能力

- `GET /api/dashboard/overview`：总览 KPI。
- `GET /api/dashboard/recommendation-funnel`：推荐漏斗和趋势。
- `GET /api/dashboard/product-selection`：选品分层和商品风险。
- `GET /api/dashboard/user-profiles`：用户画像分布。
- `GET /api/dashboard/inventory-health`：库存健康。
- `GET /api/inventory/warnings`：库存预警列表。
- `POST /api/inventory/warnings/run`：运行库存预警工作流。
- `POST /api/inventory/replenishment/suggest`：生成补货建议和补货单。
- `POST /api/inventory/events`：处理库存变更事件，支持 `event_id` 幂等。

### 2.2 已有前端基础

- 前端目录：`web/`。
- 当前主页面：`web/src/pages/DashboardHome.vue`。
- 当前接口封装：`web/src/api/dashboard.ts`。
- 当前类型定义：`web/src/types/dashboard.ts`。
- 当前全局风格：`web/src/styles.css`。
- 当前技术栈：Vue 3 + TypeScript + ECharts。
- 当前视觉风格：深蓝背景、青蓝发光边框、黄色关键数值、半透明面板。

## 3. 页面信息架构

参考示例图的左侧按钮式导航，但保留本项目当前配色和大屏质感。导航不改变业务口径，只负责把现有模块拆成可独立查看的页面。

### 3.1 左侧导航按钮

建议页面：

- `总览`：核心指标、综合质量指数、快捷入口。
- `推荐`：推荐漏斗、推荐趋势、场景表现。
- `选品`：商品分层、选品得分排行、风险商品。
- `画像`：用户阶段、标签偏好、类目偏好、价格偏好。
- `库存`：库存健康、类目库存、风险商品。
- `预警`：第三阶段库存预警列表、预警等级分布、触发工作流按钮。
- `补货`：第三阶段补货建议、补货单状态、补货操作面板。
- `工作流`：库存预警和自动补货运行记录。

### 3.2 顶部区域

保留现有顶部标题区和筛选区，但将其变为多页面共享：

- 租户 ID。
- 商家 ID。
- 时间范围。
- 场景。
- 请求 ID。
- 演示模式 / 真实模式。
- 刷新数据。
- 重置筛选。

### 3.3 主内容区域

主内容根据左侧按钮切换，不跳转路由也可以实现。第一版建议在 `DashboardHome.vue` 内维护 `activePage`，后续页面复杂后再拆成 `DashboardLayout.vue` 和多个子页面组件。

## 4. 第三阶段功能接入设计

### 4.1 库存预警页

数据来源：

- `GET /api/inventory/warnings`
- `POST /api/inventory/warnings/run`
- `GET /api/dashboard/inventory-health`

核心组件：

- 预警 KPI：高风险数、严重风险数、待处理数、已关闭数。
- 预警等级分布图：`critical`、`high`、`medium`、`healthy`。
- 预警列表：商品、类目、预警等级、状态、预计日销、预计缺货天数、建议动作。
- 操作按钮：运行预警、按等级筛选、按状态筛选。

交互规则：

- 点击 `运行预警` 调用 `POST /api/inventory/warnings/run`。
- 运行成功后刷新预警列表和库存健康数据。
- 列表行提供 `生成补货建议` 入口，切换到补货页并带入 `product_id` 与 `warning_id`。

### 4.2 补货页

数据来源：

- `POST /api/inventory/replenishment/suggest`
- `GET /api/inventory/warnings`
- 后续可增加补货单列表查询接口。

核心组件：

- 补货建议表单：商品 ID、预测天数、是否持久化。
- 建议结果卡片：建议补货量、目标库存、有效库存、预计日销、建议动作。
- 风险说明：销量不足、长尾商品、低价值分等。
- 状态展示：`draft`、`pending_approval`、`approved`、`rejected`、`purchasing`、`in_transit`、`received`、`closed`。

交互规则：

- 从预警列表进入时自动带入商品 ID。
- 点击 `生成建议` 调用 `POST /api/inventory/replenishment/suggest`。
- 结果中若返回 `replenishment_order_id`，在页面展示补货单编号和状态。

### 4.3 工作流页

第一版可先使用第三阶段接口返回的 `run_id` 在前端展示最近操作结果。若需要完整历史记录，再补充后端只读接口读取 MongoDB `workflow_runs`。

建议后续接口：

- `GET /api/workflows/runs`

建议字段：

- `tenant_id`
- `merchant_id`
- `workflow_name`
- `run_id`
- `request_id`
- `status`
- `started_at`
- `finished_at`
- `error_message`

## 5. 前端实施步骤

### 步骤一：扩展接口和类型

修改文件：

- `web/src/types/dashboard.ts`
- `web/src/api/dashboard.ts`

新增类型：

- `InventoryWarningItem`
- `InventoryWarningsData`
- `RunInventoryWarningsPayload`
- `ReplenishmentSuggestPayload`
- `ReplenishmentSuggestData`

新增接口函数：

- `fetchInventoryWarnings(filters)`
- `runInventoryWarnings(payload)`
- `suggestReplenishment(payload)`

演示模式要求：

- 补齐第三阶段 demo 数据，保证无后端时可直接查看多页面 UI。

### 步骤二：改造页面布局

修改文件：

- `web/src/pages/DashboardHome.vue`
- `web/src/styles.css`

新增结构：

- `.dashboard-layout`
- `.side-nav`
- `.side-nav-button`
- `.dashboard-content`
- `.page-section`

保留结构：

- 现有 `.panel`
- 现有 `.ghost-btn`
- 现有 `.primary-btn`
- 现有深蓝 / 青蓝 / 黄色高亮配色。

### 步骤三：拆分页面展示

第一版可在同一个 Vue 文件内按 `activePage` 条件渲染：

- `overview`
- `recommendation`
- `selection`
- `profile`
- `inventory`
- `warning`
- `replenishment`
- `workflow`

验收后再按维护性拆成组件：

- `DashboardOverview.vue`
- `RecommendationDashboard.vue`
- `ProductSelectionDashboard.vue`
- `UserProfileDashboard.vue`
- `InventoryDashboard.vue`
- `InventoryWarningDashboard.vue`
- `ReplenishmentDashboard.vue`
- `WorkflowDashboard.vue`

### 步骤四：接入第三阶段操作

实现交互：

- 预警页运行库存预警。
- 预警页刷新预警列表。
- 预警行跳转补货页。
- 补货页生成补货建议。
- 操作成功后展示 `run_id`、补货单 ID、状态和风险说明。

### 步骤五：图表与表格补齐

新增图表：

- 预警等级分布图。
- 补货建议状态分布图。
- 缺货天数排行。

新增表格：

- 库存预警列表。
- 补货建议结果表。
- 最近工作流运行结果。

### 步骤六：验证与回归

后端验证：

- `python3 -m pytest`

前端验证：

- `npm run build`
- 使用浏览器查看多页面切换、图表非空、按钮可点击、移动端不重叠。

## 6. 视觉约束

- 不改变当前深蓝、青蓝、霓虹青绿、黄色高亮的主配色。
- 左侧按钮使用图标或短标签，避免长文本挤压。
- 面板仍使用当前半透明背景、发光边框和扫描线效果。
- 不引入浅色后台风格。
- 不引入新的大面积紫色、米色或棕橙色主题。
- 多页面切换不应造成图表容器高度跳动。
- 表格在窄屏下允许横向滚动，不允许文字互相覆盖。

## 7. 验收标准

- 看板左侧出现多页面按钮，能在各模块间切换。
- 第三阶段库存预警可以在看板中查询和触发。
- 第三阶段补货建议可以在看板中生成并展示结果。
- 原有总览、推荐、选品、画像、库存页面功能不丢失。
- 配色、面板、按钮和图表风格与当前看板一致。
- 演示模式下无需后端即可查看预警和补货页面。
- 真实模式下接口错误有可见提示，不造成页面空白。
- 前后端测试和构建通过。

## 8. 建议实施顺序

1. 先补前端类型、接口和 demo 数据。
2. 再加左侧导航和页面切换骨架。
3. 将现有总览内容拆到 `总览` 页。
4. 将推荐、选品、画像、库存内容分配到独立页面。
5. 接入预警页的查询和运行工作流。
6. 接入补货页的建议生成。
7. 增加工作流最近运行结果展示。
8. 执行后端测试、前端构建和浏览器视觉检查。
