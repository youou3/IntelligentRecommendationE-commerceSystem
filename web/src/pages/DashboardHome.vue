<template>
  <main class="dashboard-shell">
    <div class="scanline"></div>

    <div class="dashboard-layout">
      <aside class="side-nav panel">
        <div class="nav-mark">IR</div>
        <button
          v-for="page in pages"
          :key="page.key"
          class="side-nav-button"
          :class="{ active: activePage === page.key }"
          :title="page.label"
          @click="setActivePage(page.key)"
        >
          <span class="nav-icon">{{ page.icon }}</span>
          <span class="nav-label">{{ page.label }}</span>
        </button>
      </aside>

      <div class="dashboard-content">
        <header class="dashboard-topbar panel">
          <div class="title-group">
            <div class="eyebrow">QUALITY CONTROL CENTER</div>
            <div class="title-row">
              <h1>智能推荐运营看板</h1>
              <span class="mode-badge" :class="demoMode ? 'demo' : 'live'">
                {{ demoMode ? 'DEMO MODE' : 'LIVE MODE' }}
              </span>
            </div>
            <p>{{ activePageMeta.description }}</p>
          </div>

          <div class="topbar-actions">
            <button class="ghost-btn" @click="reloadAll">刷新数据</button>
            <button class="ghost-btn" :class="{ active: demoMode }" @click="toggleDemoMode">
              {{ demoMode ? '切换真实模式' : '切换演示模式' }}
            </button>
            <button class="ghost-btn" @click="resetFilters">重置筛选</button>
          </div>
        </header>

        <section class="panel control-panel">
          <div class="filter-grid">
            <label>
              <span>租户 ID</span>
              <input v-model="filters.tenant_id" placeholder="T1" />
            </label>
            <label>
              <span>商家 ID</span>
              <input v-model="filters.merchant_id" placeholder="M1" />
            </label>
            <label>
              <span>开始日期</span>
              <input v-model="filters.start_date" type="date" />
            </label>
            <label>
              <span>结束日期</span>
              <input v-model="filters.end_date" type="date" />
            </label>
            <label>
              <span>场景</span>
              <select v-model="filters.scene">
                <option value="">全部场景</option>
                <option value="home">首页</option>
                <option value="detail">详情页</option>
                <option value="cart">购物车</option>
              </select>
            </label>
            <label>
              <span>请求 ID</span>
              <input v-model="filters.request_id" placeholder="REQ_DASH_1" />
            </label>
          </div>

          <div class="preset-row">
            <button class="ghost-btn" @click="setRange(7)">7 天</button>
            <button class="ghost-btn" @click="setRange(30)">30 天</button>
            <button class="ghost-btn" @click="setScene('home')">首页</button>
            <button class="ghost-btn" @click="setScene('detail')">详情页</button>
            <button class="ghost-btn" @click="setScene('cart')">购物车</button>
            <button class="ghost-btn" @click="setDemoHealthy">健康演示</button>
            <button class="ghost-btn" @click="setDemoRisk">风险库存演示</button>
            <button class="primary-btn" @click="reloadAll">应用筛选</button>
          </div>
        </section>

        <div v-if="pageError" class="panel status-strip error">{{ pageError }}</div>
        <div v-if="actionMessage" class="panel status-strip">{{ actionMessage }}</div>

        <section v-if="activePage === 'overview'" class="page-section">
          <section class="top-grid">
            <article class="panel summary-panel">
              <div class="panel-head">
                <h2>核心指标</h2>
                <span>当前周期</span>
              </div>
              <div class="kpi-grid compact">
                <div v-for="item in kpiCards" :key="item.label" class="mini-kpi">
                  <div class="mini-kpi-label">{{ item.label }}</div>
                  <div class="mini-kpi-value">{{ item.value }}</div>
                  <div class="mini-kpi-sub">{{ item.sub }}</div>
                </div>
              </div>
            </article>

            <article class="panel center-panel">
              <div class="panel-head">
                <h2>综合质量指数</h2>
                <span>CTR / 转化率 / 库存健康</span>
              </div>
              <div ref="gaugeEl" class="chart-box center-chart"></div>
              <div class="center-metrics">
                <div>
                  <span>CTR</span>
                  <strong>{{ formatPercent(overview?.kpis.ctr ?? 0) }}</strong>
                </div>
                <div>
                  <span>转化率</span>
                  <strong>{{ formatPercent(overview?.kpis.conversion_rate ?? 0) }}</strong>
                </div>
                <div>
                  <span>低库存</span>
                  <strong>{{ overview?.kpis.low_stock_products ?? 0 }}</strong>
                </div>
              </div>
            </article>

            <article class="panel summary-panel">
              <div class="panel-head">
                <h2>第三阶段入口</h2>
                <span>预警 / 补货</span>
              </div>
              <div class="shortcut-grid">
                <button class="ghost-btn shortcut" @click="setActivePage('warning')">库存预警</button>
                <button class="ghost-btn shortcut" @click="setActivePage('replenishment')">补货建议</button>
                <button class="ghost-btn shortcut" @click="runWarningWorkflow">运行预警</button>
                <button class="ghost-btn shortcut" @click="setActivePage('workflow')">工作流记录</button>
              </div>
            </article>
          </section>
        </section>

        <section v-if="activePage === 'recommendation'" class="page-section main-grid">
          <article class="panel chart-card tall">
            <div class="panel-head">
              <h2>推荐漏斗</h2>
              <span>曝光 → 点击 → 加购 → 转化</span>
            </div>
            <div ref="funnelEl" class="chart-box"></div>
          </article>
          <article class="panel chart-card wide">
            <div class="panel-head">
              <h2>推荐趋势</h2>
              <span>按天统计推荐请求与反馈</span>
            </div>
            <div ref="trendEl" class="chart-box"></div>
          </article>
          <article class="panel table-card">
            <div class="panel-head">
              <h2>场景表现</h2>
              <span>推荐质量对比</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>场景</th>
                  <th>曝光</th>
                  <th>点击</th>
                  <th>加购</th>
                  <th>转化</th>
                  <th>CTR</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in funnel?.by_scene || []" :key="String(row.scene)">
                  <td>{{ row.scene }}</td>
                  <td>{{ row.exposures }}</td>
                  <td>{{ row.clicks }}</td>
                  <td>{{ row.add_carts }}</td>
                  <td>{{ row.conversions }}</td>
                  <td>{{ formatPercent(row.ctr) }}</td>
                </tr>
              </tbody>
            </table>
          </article>
        </section>

        <section v-if="activePage === 'selection'" class="page-section main-grid">
          <article class="panel chart-card tall">
            <div class="panel-head">
              <h2>商品分层</h2>
              <span>hot / potential / long_tail / risk</span>
            </div>
            <div ref="layerEl" class="chart-box"></div>
          </article>
          <article class="panel table-card wide-table">
            <div class="panel-head">
              <h2>商品健康表</h2>
              <span>选品与库存联动</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>商品</th>
                  <th>分层</th>
                  <th>评分</th>
                  <th>库存</th>
                  <th>CTR</th>
                  <th>转化率</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in selectionRows" :key="String(row.product_id)">
                  <td>{{ row.name }}</td>
                  <td><span class="tag" :class="String(row.layer)">{{ row.layer }}</span></td>
                  <td>{{ formatNumber(row.selection_score) }}</td>
                  <td>{{ row.effective_stock }}</td>
                  <td>{{ formatPercent(row.ctr) }}</td>
                  <td>{{ formatPercent(row.conversion_rate) }}</td>
                </tr>
              </tbody>
            </table>
          </article>
        </section>

        <section v-if="activePage === 'profile'" class="page-section main-grid">
          <article class="panel chart-card tall">
            <div class="panel-head">
              <h2>用户阶段</h2>
              <span>画像分布</span>
            </div>
            <div ref="stageEl" class="chart-box"></div>
          </article>
          <article class="panel table-card">
            <div class="panel-head">
              <h2>标签偏好</h2>
              <span>Top tags</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>标签</th>
                  <th>权重</th>
                  <th>用户数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in profiles?.top_tags || []" :key="String(row.tag)">
                  <td>{{ row.tag }}</td>
                  <td>{{ formatNumber(row.weight) }}</td>
                  <td>{{ row.user_count }}</td>
                </tr>
              </tbody>
            </table>
          </article>
          <article class="panel table-card">
            <div class="panel-head">
              <h2>类目偏好</h2>
              <span>Top categories</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>类目</th>
                  <th>权重</th>
                  <th>用户数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in profiles?.top_categories || []" :key="String(row.category_id)">
                  <td>{{ row.category_id }}</td>
                  <td>{{ formatNumber(row.weight) }}</td>
                  <td>{{ row.user_count }}</td>
                </tr>
              </tbody>
            </table>
          </article>
        </section>

        <section v-if="activePage === 'inventory'" class="page-section main-grid">
          <article class="panel chart-card tall">
            <div class="panel-head">
              <h2>类目库存</h2>
              <span>有效库存 / 风险数</span>
            </div>
            <div ref="categoryStockEl" class="chart-box"></div>
          </article>
          <article class="panel table-card wide-table">
            <div class="panel-head">
              <h2>库存风险</h2>
              <span>低库存 / 缺货 / 异常</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>商品</th>
                  <th>风险</th>
                  <th>可用库存</th>
                  <th>锁定</th>
                  <th>有效库存</th>
                  <th>安全库存</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in inventoryRows" :key="String(row.product_id)">
                  <td>{{ row.name }}</td>
                  <td><span class="tag risk">{{ row.risk_level }}</span></td>
                  <td>{{ row.available_stock }}</td>
                  <td>{{ row.locked_stock }}</td>
                  <td>{{ row.effective_stock }}</td>
                  <td>{{ row.safe_stock }}</td>
                </tr>
              </tbody>
            </table>
          </article>
        </section>

        <section v-if="activePage === 'warning'" class="page-section">
          <section class="top-grid">
            <article class="panel summary-panel">
              <div class="panel-head">
                <h2>预警概览</h2>
                <span>第三阶段</span>
              </div>
              <div class="kpi-grid compact">
                <div v-for="item in warningKpis" :key="item.label" class="mini-kpi">
                  <div class="mini-kpi-label">{{ item.label }}</div>
                  <div class="mini-kpi-value">{{ item.value }}</div>
                  <div class="mini-kpi-sub">{{ item.sub }}</div>
                </div>
              </div>
            </article>
            <article class="panel chart-card tall">
              <div class="panel-head">
                <h2>预警等级</h2>
                <span>critical / high / medium</span>
              </div>
              <div ref="warningLevelEl" class="chart-box"></div>
            </article>
            <article class="panel summary-panel">
              <div class="panel-head">
                <h2>预警操作</h2>
                <span>Workflow</span>
              </div>
              <div class="action-stack">
                <button class="primary-btn" :disabled="actionLoading" @click="runWarningWorkflow">
                  {{ actionLoading ? '运行中...' : '运行库存预警' }}
                </button>
                <button class="ghost-btn" @click="reloadWarnings">刷新预警列表</button>
                <button class="ghost-btn" @click="setActivePage('replenishment')">进入补货建议</button>
              </div>
            </article>
          </section>

          <article class="panel table-card">
            <div class="panel-head">
              <h2>库存预警列表</h2>
              <span>{{ warningData?.total ?? warningRows.length }} 条记录</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>商品</th>
                  <th>等级</th>
                  <th>状态</th>
                  <th>预计日销</th>
                  <th>缺货天数</th>
                  <th>建议动作</th>
                  <th>原因</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in warningRows" :key="`${row.product_id}-${row.id || row.warning_level}`">
                  <td>{{ row.product_name || row.product_id }}</td>
                  <td><span class="tag" :class="row.warning_level">{{ row.warning_level }}</span></td>
                  <td>{{ row.status }}</td>
                  <td>{{ formatNumber(row.forecast_daily_sales) }}</td>
                  <td>{{ row.stockout_days ?? '-' }}</td>
                  <td>{{ row.suggested_action }}</td>
                  <td>{{ row.warning_reason.join(', ') }}</td>
                  <td><button class="ghost-btn mini-action" @click="suggestForWarning(row)">生成补货</button></td>
                </tr>
              </tbody>
            </table>
          </article>
        </section>

        <section v-if="activePage === 'replenishment'" class="page-section main-grid">
          <article class="panel summary-panel">
            <div class="panel-head">
              <h2>补货复盘</h2>
              <span>第五阶段</span>
            </div>
            <div class="kpi-grid compact">
              <div class="mini-kpi">
                <div class="mini-kpi-label">补货单</div>
                <div class="mini-kpi-value">{{ replenishmentReview?.summary.replenishment_orders ?? 0 }}</div>
                <div class="mini-kpi-sub">周期内生成</div>
              </div>
              <div class="mini-kpi">
                <div class="mini-kpi-label">建议数量</div>
                <div class="mini-kpi-value">{{ replenishmentReview?.summary.suggested_quantity ?? 0 }}</div>
                <div class="mini-kpi-sub">suggested</div>
              </div>
              <div class="mini-kpi">
                <div class="mini-kpi-label">审批率</div>
                <div class="mini-kpi-value">{{ formatPercent(replenishmentReview?.summary.approval_rate ?? 0) }}</div>
                <div class="mini-kpi-sub">approved / total</div>
              </div>
              <div class="mini-kpi">
                <div class="mini-kpi-label">入库率</div>
                <div class="mini-kpi-value">{{ formatPercent(replenishmentReview?.summary.receive_rate ?? 0) }}</div>
                <div class="mini-kpi-sub">received / total</div>
              </div>
            </div>
          </article>

          <article class="panel summary-panel">
            <div class="panel-head">
              <h2>补货建议</h2>
              <span>自动补货 WORKFLOW</span>
            </div>
            <div class="form-stack">
              <label>
                <span>商品 ID</span>
                <input v-model="replenishmentForm.product_id" placeholder="P10009" />
              </label>
              <label>
                <span>预测天数</span>
                <input v-model.number="replenishmentForm.forecast_days" type="number" min="1" max="90" />
              </label>
              <label class="check-row">
                <input v-model="replenishmentForm.persist" type="checkbox" />
                <span>生成补货单</span>
              </label>
              <button class="primary-btn" :disabled="actionLoading" @click="generateReplenishment">
                {{ actionLoading ? '生成中...' : '生成建议' }}
              </button>
            </div>
          </article>

          <article class="panel chart-card tall">
            <div class="panel-head">
              <h2>缺货天数排行</h2>
              <span>预警商品</span>
            </div>
            <div ref="stockoutEl" class="chart-box"></div>
          </article>

          <article class="panel summary-panel result-panel">
            <div class="panel-head">
              <h2>建议结果</h2>
              <span>{{ replenishmentResult?.status || '等待生成' }}</span>
            </div>
            <div v-if="replenishmentResult" class="result-grid">
              <div>
                <span>建议补货量</span>
                <strong>{{ replenishmentResult.suggest_quantity }}</strong>
              </div>
              <div>
                <span>目标库存</span>
                <strong>{{ replenishmentResult.target_stock }}</strong>
              </div>
              <div>
                <span>有效库存</span>
                <strong>{{ replenishmentResult.effective_stock }}</strong>
              </div>
              <div>
                <span>预计日销</span>
                <strong>{{ formatNumber(replenishmentResult.daily_sales) }}</strong>
              </div>
              <div>
                <span>补货单</span>
                <strong>{{ replenishmentResult.replenishment_order_id || '-' }}</strong>
              </div>
              <div>
                <span>Run ID</span>
                <strong class="small-strong">{{ replenishmentResult.run_id }}</strong>
              </div>
            </div>
            <div v-else class="empty-state">从预警列表选择商品，或输入商品 ID 生成补货建议。</div>
            <div v-if="replenishmentResult" class="reason-list">
              <span v-for="reason in replenishmentResult.reason" :key="reason" class="tag potential">{{ reason }}</span>
              <span v-for="risk in replenishmentResult.risk_note" :key="risk" class="tag risk">{{ risk }}</span>
            </div>
          </article>

          <article class="panel table-card wide-table">
            <div class="panel-head">
              <h2>补货效果复盘</h2>
              <span>建议 / 审批 / 销售</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>商品</th>
                  <th>状态</th>
                  <th>建议量</th>
                  <th>审批量</th>
                  <th>有效库存</th>
                  <th>销量</th>
                  <th>采纳率</th>
                  <th>售罄率</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in replenishmentReview?.items || []" :key="String(row.replenishment_order_id)">
                  <td>{{ row.product_name || row.product_id }}</td>
                  <td><span class="tag potential">{{ row.status }}</span></td>
                  <td>{{ row.suggest_quantity }}</td>
                  <td>{{ row.approved_quantity ?? '-' }}</td>
                  <td>{{ row.effective_stock }}</td>
                  <td>{{ row.sold_quantity }}</td>
                  <td>{{ formatPercent(row.fulfill_rate) }}</td>
                  <td>{{ formatPercent(row.sell_through_rate) }}</td>
                </tr>
              </tbody>
            </table>
          </article>
        </section>

        <section v-if="activePage === 'workflow'" class="page-section">
          <section class="top-grid">
            <article class="panel summary-panel">
              <div class="panel-head">
                <h2>运营复盘</h2>
                <span>推荐 / 画像 / 库存</span>
              </div>
              <div class="kpi-grid compact">
                <div class="mini-kpi">
                  <div class="mini-kpi-label">推荐转化率</div>
                  <div class="mini-kpi-value">{{ formatPercent(operationsReview?.summary.recommendation_conversion_rate ?? 0) }}</div>
                  <div class="mini-kpi-sub">convert / exposure</div>
                </div>
                <div class="mini-kpi">
                  <div class="mini-kpi-label">画像覆盖</div>
                  <div class="mini-kpi-value">{{ formatPercent(operationsReview?.summary.profile_coverage ?? 0) }}</div>
                  <div class="mini-kpi-sub">profiled users</div>
                </div>
                <div class="mini-kpi">
                  <div class="mini-kpi-label">风险商品</div>
                  <div class="mini-kpi-value">{{ operationsReview?.summary.risk_products ?? 0 }}</div>
                  <div class="mini-kpi-sub">selection risk</div>
                </div>
                <div class="mini-kpi">
                  <div class="mini-kpi-label">低库存</div>
                  <div class="mini-kpi-value">{{ operationsReview?.summary.low_stock_products ?? 0 }}</div>
                  <div class="mini-kpi-sub">inventory risk</div>
                </div>
              </div>
            </article>

            <article class="panel summary-panel">
              <div class="panel-head">
                <h2>MCP 健康</h2>
                <span>SKILL 调用</span>
              </div>
              <div class="kpi-grid compact">
                <div class="mini-kpi">
                  <div class="mini-kpi-label">调用数</div>
                  <div class="mini-kpi-value">{{ operationsReview?.summary.skill_calls ?? 0 }}</div>
                  <div class="mini-kpi-sub">skill_call_logs</div>
                </div>
                <div class="mini-kpi">
                  <div class="mini-kpi-label">失败</div>
                  <div class="mini-kpi-value">{{ operationsReview?.summary.skill_failed_calls ?? 0 }}</div>
                  <div class="mini-kpi-sub">failed</div>
                </div>
                <div class="mini-kpi">
                  <div class="mini-kpi-label">降级</div>
                  <div class="mini-kpi-value">{{ operationsReview?.summary.skill_fallback_calls ?? 0 }}</div>
                  <div class="mini-kpi-sub">fallback</div>
                </div>
                <div class="mini-kpi">
                  <div class="mini-kpi-label">平均耗时</div>
                  <div class="mini-kpi-value">{{ operationsReview?.summary.avg_skill_cost_ms ?? 0 }}</div>
                  <div class="mini-kpi-sub">ms</div>
                </div>
              </div>
            </article>

            <article class="panel summary-panel">
              <div class="panel-head">
                <h2>工作流健康</h2>
                <span>workflow_runs</span>
              </div>
              <div class="kpi-grid compact">
                <div class="mini-kpi">
                  <div class="mini-kpi-label">运行次数</div>
                  <div class="mini-kpi-value">{{ operationsReview?.summary.workflow_runs ?? 0 }}</div>
                  <div class="mini-kpi-sub">total</div>
                </div>
                <div class="mini-kpi">
                  <div class="mini-kpi-label">失败运行</div>
                  <div class="mini-kpi-value">{{ operationsReview?.summary.workflow_failed_runs ?? 0 }}</div>
                  <div class="mini-kpi-sub">failed</div>
                </div>
              </div>
            </article>
          </section>

          <article class="panel table-card">
            <div class="panel-head">
              <h2>最近工作流结果</h2>
              <span>本次会话 + 后端复盘</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>工作流</th>
                  <th>Run ID</th>
                  <th>请求 ID</th>
                  <th>状态</th>
                  <th>摘要</th>
                  <th>时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in workflowRuns" :key="row.run_id">
                  <td>{{ row.workflow_name }}</td>
                  <td>{{ row.run_id }}</td>
                  <td>{{ row.request_id }}</td>
                  <td><span class="tag potential">{{ row.status }}</span></td>
                  <td>{{ row.summary }}</td>
                  <td>{{ row.created_at }}</td>
                </tr>
                <tr v-if="workflowRuns.length === 0">
                  <td colspan="6">暂无本次会话运行记录，可查看上方后端复盘指标。</td>
                </tr>
              </tbody>
            </table>
          </article>
        </section>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import * as echarts from 'echarts'
import {
  fetchFunnel,
  fetchInventory,
  fetchInventoryWarnings,
  fetchOperationsReview,
  fetchOverview,
  fetchProfiles,
  fetchReplenishmentReview,
  fetchSelection,
  runInventoryWarnings,
  suggestReplenishment,
} from '../api/dashboard'
import type {
  DashboardFilters,
  FunnelData,
  InventoryHealthData,
  InventoryWarningItem,
  InventoryWarningsData,
  OperationsReviewData,
  OverviewData,
  ReplenishmentReviewData,
  ReplenishmentSuggestData,
  SelectionData,
  UserProfileData,
  WorkflowRunView,
} from '../types/dashboard'

type PageKey = 'overview' | 'recommendation' | 'selection' | 'profile' | 'inventory' | 'warning' | 'replenishment' | 'workflow'

const STORAGE_KEY = 'ir_dashboard_demo_mode'
const demoMode = ref(localStorage.getItem(STORAGE_KEY) !== 'false')
const filters = reactive<DashboardFilters>(createDefaultFilters())
const activePage = ref<PageKey>('overview')
const actionLoading = ref(false)
const pageError = ref('')
const actionMessage = ref('')

const pages: Array<{ key: PageKey; label: string; icon: string; description: string }> = [
  { key: 'overview', label: '总览', icon: '⌂', description: '核心指标、综合质量指数与第三阶段快捷入口' },
  { key: 'recommendation', label: '推荐', icon: '↗', description: '推荐漏斗、趋势和场景表现' },
  { key: 'selection', label: '选品', icon: '◆', description: '商品分层、选品得分和运营风险' },
  { key: 'profile', label: '画像', icon: '◎', description: '用户阶段、标签偏好和类目偏好' },
  { key: 'inventory', label: '库存', icon: '▣', description: '库存健康、类目库存和风险商品' },
  { key: 'warning', label: '预警', icon: '!', description: '第三阶段库存预警列表和工作流触发' },
  { key: 'replenishment', label: '补货', icon: '+', description: '第三阶段补货建议与补货单状态' },
  { key: 'workflow', label: '工作流', icon: '≈', description: '预警与补货工作流最近运行结果' },
]

const overview = ref<OverviewData | null>(null)
const funnel = ref<FunnelData | null>(null)
const selection = ref<SelectionData | null>(null)
const profiles = ref<UserProfileData | null>(null)
const inventory = ref<InventoryHealthData | null>(null)
const warningData = ref<InventoryWarningsData | null>(null)
const replenishmentReview = ref<ReplenishmentReviewData | null>(null)
const operationsReview = ref<OperationsReviewData | null>(null)
const replenishmentResult = ref<ReplenishmentSuggestData | null>(null)
const workflowRuns = ref<WorkflowRunView[]>([])

const replenishmentForm = reactive({
  product_id: '',
  forecast_days: 14,
  warning_id: undefined as number | undefined,
  persist: true,
})

const funnelEl = ref<HTMLDivElement | null>(null)
const layerEl = ref<HTMLDivElement | null>(null)
const stageEl = ref<HTMLDivElement | null>(null)
const trendEl = ref<HTMLDivElement | null>(null)
const gaugeEl = ref<HTMLDivElement | null>(null)
const categoryStockEl = ref<HTMLDivElement | null>(null)
const warningLevelEl = ref<HTMLDivElement | null>(null)
const stockoutEl = ref<HTMLDivElement | null>(null)

const activePageMeta = computed(() => pages.find((page) => page.key === activePage.value) || pages[0])

const kpiCards = computed(() => {
  const kpis = overview.value?.kpis || {}
  return [
    { label: '行为事件', value: kpis.behavior_events ?? 0, sub: '行为采集量' },
    { label: '推荐请求', value: kpis.recommendation_requests ?? 0, sub: '推荐链路请求' },
    { label: '点击率 CTR', value: formatPercent(kpis.ctr ?? 0), sub: '推荐点击效率' },
    { label: '加购率', value: formatPercent(kpis.add_cart_rate ?? 0), sub: '推荐加购效率' },
    { label: '转化率', value: formatPercent(kpis.conversion_rate ?? 0), sub: '推荐成交效率' },
    { label: '低库存商品', value: kpis.low_stock_products ?? 0, sub: '库存风险数量' },
  ]
})

const selectionRows = computed(() => selection.value?.top_products || [])
const inventoryRows = computed(() => inventory.value?.risk_products || [])
const warningRows = computed(() => warningData.value?.items || [])

const warningKpis = computed(() => {
  const rows = warningRows.value
  const critical = rows.filter((row) => row.warning_level === 'critical').length
  const high = rows.filter((row) => row.warning_level === 'high').length
  const pending = rows.filter((row) => ['pending', 'triggered', 'notified'].includes(row.status)).length
  const resolved = rows.filter((row) => ['resolved', 'closed'].includes(row.status)).length
  return [
    { label: '严重预警', value: critical, sub: 'critical' },
    { label: '高风险', value: high, sub: 'high' },
    { label: '待处理', value: pending, sub: 'pending / triggered' },
    { label: '已处理', value: resolved, sub: 'resolved / closed' },
  ]
})

function createDefaultFilters(): DashboardFilters {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 6)
  return {
    tenant_id: 'T1',
    merchant_id: 'M1',
    start_date: toDateInput(start),
    end_date: toDateInput(end),
    scene: '',
    request_id: 'REQ_DASH_1',
    page: 1,
    page_size: 20,
  }
}

function toDateInput(d: Date) {
  return d.toISOString().slice(0, 10)
}

function formatNumber(value: unknown) {
  const num = typeof value === 'number' ? value : Number(value || 0)
  return Number.isFinite(num) ? num.toFixed(4) : '0.0000'
}

function formatPercent(value: unknown) {
  const num = typeof value === 'number' ? value : Number(value || 0)
  return `${(num * 100).toFixed(1)}%`
}

function setActivePage(page: PageKey) {
  activePage.value = page
}

function setRange(days: number) {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - (days - 1))
  filters.start_date = toDateInput(start)
  filters.end_date = toDateInput(end)
  reloadAll()
}

function setScene(scene: string) {
  filters.scene = scene
  reloadAll()
}

function setDemoHealthy() {
  demoMode.value = true
  localStorage.setItem(STORAGE_KEY, 'true')
  filters.scene = ''
  reloadAll()
}

function setDemoRisk() {
  demoMode.value = true
  localStorage.setItem(STORAGE_KEY, 'true')
  filters.scene = 'cart'
  reloadAll()
}

function resetFilters() {
  Object.assign(filters, createDefaultFilters())
  reloadAll()
}

function toggleDemoMode() {
  demoMode.value = !demoMode.value
  localStorage.setItem(STORAGE_KEY, String(demoMode.value))
  reloadAll()
}

async function reloadAll() {
  pageError.value = ''
  actionMessage.value = ''
  const nextFilters = { ...filters }
  try {
    const [overviewData, funnelData, selectionData, profileData, inventoryData, warnings, replenishmentReviewData, operationsReviewData] = await Promise.all([
      fetchOverview(nextFilters),
      fetchFunnel(nextFilters),
      fetchSelection(nextFilters),
      fetchProfiles(nextFilters),
      fetchInventory(nextFilters),
      fetchInventoryWarnings(nextFilters),
      fetchReplenishmentReview(nextFilters),
      fetchOperationsReview(nextFilters),
    ])
    overview.value = overviewData
    funnel.value = funnelData
    selection.value = selectionData
    profiles.value = profileData
    inventory.value = inventoryData
    warningData.value = warnings
    replenishmentReview.value = replenishmentReviewData
    operationsReview.value = operationsReviewData
    await nextTick()
    renderCharts()
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : '加载看板数据失败'
  }
}

async function reloadWarnings() {
  pageError.value = ''
  try {
    warningData.value = await fetchInventoryWarnings({ ...filters })
    await nextTick()
    renderCharts()
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : '刷新预警列表失败'
  }
}

async function runWarningWorkflow() {
  actionLoading.value = true
  pageError.value = ''
  actionMessage.value = ''
  try {
    const result = await runInventoryWarnings({
      tenant_id: filters.tenant_id,
      merchant_id: filters.merchant_id,
      request_id: filters.request_id || `REQ-WARNING-${Date.now()}`,
      sales_days: 7,
      persist: true,
    })
    warningData.value = result
    actionMessage.value = `库存预警已运行，Run ID：${result.run_id || '-'}`
    workflowRuns.value.unshift({
      workflow_name: 'inventory_warning',
      run_id: result.run_id || `RUN-${Date.now()}`,
      request_id: filters.request_id || '-',
      status: 'success',
      summary: `识别 ${result.items.length} 条库存预警`,
      created_at: new Date().toLocaleString(),
    })
    inventory.value = await fetchInventory({ ...filters })
    await nextTick()
    renderCharts()
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : '运行库存预警失败'
  } finally {
    actionLoading.value = false
  }
}

function suggestForWarning(row: InventoryWarningItem) {
  replenishmentForm.product_id = row.product_id
  replenishmentForm.warning_id = row.id
  activePage.value = 'replenishment'
  actionMessage.value = `已带入预警商品：${row.product_name || row.product_id}`
}

async function generateReplenishment() {
  if (!replenishmentForm.product_id) {
    pageError.value = '请先输入商品 ID'
    return
  }
  actionLoading.value = true
  pageError.value = ''
  actionMessage.value = ''
  try {
    const result = await suggestReplenishment({
      tenant_id: filters.tenant_id,
      merchant_id: filters.merchant_id,
      request_id: filters.request_id || `REQ-REPLENISH-${Date.now()}`,
      product_id: replenishmentForm.product_id,
      forecast_days: replenishmentForm.forecast_days,
      warning_id: replenishmentForm.warning_id,
      persist: replenishmentForm.persist,
    })
    replenishmentResult.value = result
    actionMessage.value = `补货建议已生成，建议数量：${result.suggest_quantity}`
    workflowRuns.value.unshift({
      workflow_name: 'auto_replenishment',
      run_id: result.run_id,
      request_id: filters.request_id || '-',
      status: 'success',
      summary: `${result.product_id} 建议补货 ${result.suggest_quantity}，状态 ${result.status}`,
      created_at: new Date().toLocaleString(),
    })
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : '生成补货建议失败'
  } finally {
    actionLoading.value = false
  }
}

function renderCharts() {
  renderGaugeChart()
  renderFunnelChart()
  renderLayerChart()
  renderStageChart()
  renderTrendChart()
  renderCategoryStockChart()
  renderWarningLevelChart()
  renderStockoutChart()
}

function renderGaugeChart() {
  if (!gaugeEl.value || !overview.value) return
  const chart = echarts.getInstanceByDom(gaugeEl.value) || echarts.init(gaugeEl.value)
  const ctr = Number(overview.value.kpis.ctr || 0)
  const conversion = Number(overview.value.kpis.conversion_rate || 0)
  const inventoryHealth = Number(overview.value.kpis.low_stock_products || 0)
  const score = Math.max(0, Math.min(100, Math.round((ctr * 50 + conversion * 30 + (1 - Math.min(inventoryHealth / 20, 1)) * 20) * 100)))
  chart.setOption({
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 210,
      endAngle: -30,
      radius: '92%',
      progress: { show: true, width: 18, itemStyle: { color: '#2dd4ff' } },
      axisLine: { lineStyle: { width: 18, color: [[1, 'rgba(75, 219, 255, 0.18)']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      title: { show: false },
      detail: {
        valueAnimation: true,
        formatter: `{value}\n综合质量指数`,
        color: '#fbff6a',
        fontSize: 28,
        fontWeight: 'bold',
        offsetCenter: [0, '12%'],
      },
      data: [{ value: score }],
    }],
  })
}

function renderFunnelChart() {
  if (!funnelEl.value || !funnel.value) return
  const chart = echarts.getInstanceByDom(funnelEl.value) || echarts.init(funnelEl.value)
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    series: [{
      type: 'funnel',
      left: '8%',
      width: '84%',
      sort: 'descending',
      label: { color: '#c7f9ff' },
      itemStyle: { borderColor: '#0f172a', borderWidth: 2 },
      data: funnel.value.funnel.map((item) => ({ name: item.label as string, value: item.count as number })),
    }],
  })
}

function renderLayerChart() {
  if (!layerEl.value || !selection.value) return
  const chart = echarts.getInstanceByDom(layerEl.value) || echarts.init(layerEl.value)
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['42%', '74%'],
      itemStyle: { borderColor: '#0f172a', borderWidth: 2 },
      label: { color: '#d8fbff' },
      data: selection.value.layer_distribution.map((item) => ({ name: item.layer, value: item.count })),
    }],
  })
}

function renderStageChart() {
  if (!stageEl.value || !profiles.value) return
  const chart = echarts.getInstanceByDom(stageEl.value) || echarts.init(stageEl.value)
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '72%'],
      itemStyle: { borderColor: '#0f172a', borderWidth: 2 },
      label: { color: '#d8fbff' },
      data: profiles.value.stage_distribution.map((item) => ({ name: item.user_stage as string, value: item.count as number })),
    }],
  })
}

function renderTrendChart() {
  if (!trendEl.value || !funnel.value) return
  const chart = echarts.getInstanceByDom(trendEl.value) || echarts.init(trendEl.value)
  const dates = funnel.value.trend.map((item) => item.date as string)
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#9ee7ff' } },
    grid: { left: 30, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: dates, axisLabel: { color: '#9ee7ff' }, axisLine: { lineStyle: { color: 'rgba(75, 219, 255, 0.35)' } } },
    yAxis: { type: 'value', axisLabel: { color: '#9ee7ff' }, splitLine: { lineStyle: { color: 'rgba(70, 140, 255, 0.15)' } } },
    series: [
      { name: '推荐请求', type: 'line', smooth: true, areaStyle: { color: 'rgba(45, 212, 255, 0.12)' }, data: funnel.value.trend.map((item) => item.recommendation_requests), lineStyle: { color: '#2dd4ff', width: 3 } },
      { name: '曝光', type: 'line', smooth: true, areaStyle: { color: 'rgba(139, 92, 246, 0.08)' }, data: funnel.value.trend.map((item) => item.exposures), lineStyle: { color: '#8b5cf6', width: 2 } },
      { name: '点击', type: 'line', smooth: true, areaStyle: { color: 'rgba(34, 197, 94, 0.08)' }, data: funnel.value.trend.map((item) => item.clicks), lineStyle: { color: '#22c55e', width: 2 } },
    ],
  })
}

function renderCategoryStockChart() {
  if (!categoryStockEl.value || !inventory.value) return
  const chart = echarts.getInstanceByDom(categoryStockEl.value) || echarts.init(categoryStockEl.value)
  const rows = inventory.value.stock_by_category
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#9ee7ff' } },
    grid: { left: 38, right: 20, top: 40, bottom: 34 },
    xAxis: { type: 'category', data: rows.map((row) => row.category_id), axisLabel: { color: '#9ee7ff' } },
    yAxis: { type: 'value', axisLabel: { color: '#9ee7ff' }, splitLine: { lineStyle: { color: 'rgba(70, 140, 255, 0.15)' } } },
    series: [
      { name: '有效库存', type: 'bar', data: rows.map((row) => row.effective_stock), itemStyle: { color: '#2dd4ff' } },
      { name: '低库存商品', type: 'bar', data: rows.map((row) => row.low_stock_products), itemStyle: { color: '#fbff6a' } },
      { name: '缺货商品', type: 'bar', data: rows.map((row) => row.out_of_stock_products), itemStyle: { color: '#fb7185' } },
    ],
  })
}

function renderWarningLevelChart() {
  if (!warningLevelEl.value || !warningData.value) return
  const chart = echarts.getInstanceByDom(warningLevelEl.value) || echarts.init(warningLevelEl.value)
  const counts = warningData.value.items.reduce<Record<string, number>>((acc, row) => {
    acc[row.warning_level] = (acc[row.warning_level] || 0) + 1
    return acc
  }, {})
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '72%'],
      label: { color: '#d8fbff' },
      itemStyle: { borderColor: '#0f172a', borderWidth: 2 },
      data: Object.entries(counts).map(([name, value]) => ({ name, value })),
    }],
  })
}

function renderStockoutChart() {
  if (!stockoutEl.value || !warningData.value) return
  const chart = echarts.getInstanceByDom(stockoutEl.value) || echarts.init(stockoutEl.value)
  const rows = [...warningData.value.items]
    .filter((row) => row.stockout_days !== null && row.stockout_days !== undefined)
    .sort((a, b) => Number(a.stockout_days || 999) - Number(b.stockout_days || 999))
    .slice(0, 8)
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: 90, right: 20, top: 24, bottom: 24 },
    xAxis: { type: 'value', axisLabel: { color: '#9ee7ff' }, splitLine: { lineStyle: { color: 'rgba(70, 140, 255, 0.15)' } } },
    yAxis: { type: 'category', data: rows.map((row) => row.product_name || row.product_id), axisLabel: { color: '#9ee7ff' } },
    series: [{ name: '缺货天数', type: 'bar', data: rows.map((row) => row.stockout_days), itemStyle: { color: '#fbff6a' } }],
  })
}

watch(activePage, async () => {
  await nextTick()
  renderCharts()
})

onMounted(() => {
  reloadAll()
})
</script>
