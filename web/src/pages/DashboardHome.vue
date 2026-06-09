<template>
  <main class="dashboard-shell">
    <div class="scanline"></div>

    <header class="dashboard-topbar panel">
      <div class="title-group">
        <div class="eyebrow">QUALITY CONTROL CENTER</div>
        <div class="title-row">
          <h1>质量管控中心</h1>
          <span class="mode-badge" :class="demoMode ? 'demo' : 'live'">
            {{ demoMode ? 'DEMO MODE' : 'LIVE MODE' }}
          </span>
        </div>
        <p>推荐、选品、画像、库存四大模块可视化联动</p>
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
        <button class="ghost-btn" @click="setDemoLowStock">低库存演示</button>
        <button class="ghost-btn" @click="setDemoHot">高转化演示</button>
        <button class="ghost-btn" @click="setDemoRisk">风险库存演示</button>
        <button class="primary-btn" @click="reloadAll">应用筛选</button>
      </div>
    </section>

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
          <h2>测试快捷按钮</h2>
          <span>高频验证场景</span>
        </div>
        <div class="shortcut-grid">
          <button class="ghost-btn shortcut" @click="setDemoHealthy">健康商品</button>
          <button class="ghost-btn shortcut" @click="setDemoHot">高转化商品</button>
          <button class="ghost-btn shortcut" @click="setDemoRisk">风险库存</button>
          <button class="ghost-btn shortcut" @click="setDemoHomeScene">首页场景</button>
          <button class="ghost-btn shortcut" @click="setDemoDetailScene">详情场景</button>
          <button class="ghost-btn shortcut" @click="setDemoCartScene">购物车场景</button>
        </div>
      </article>
    </section>

    <section class="main-grid">
      <article class="panel chart-card tall">
        <div class="panel-head">
          <h2>推荐漏斗</h2>
          <span>曝光 → 点击 → 加购 → 转化</span>
        </div>
        <div ref="funnelEl" class="chart-box"></div>
      </article>

      <article class="panel chart-card tall">
        <div class="panel-head">
          <h2>商品分层</h2>
          <span>hot / potential / long_tail / risk</span>
        </div>
        <div ref="layerEl" class="chart-box"></div>
      </article>

      <article class="panel chart-card tall">
        <div class="panel-head">
          <h2>用户阶段</h2>
          <span>画像分布</span>
        </div>
        <div ref="stageEl" class="chart-box"></div>
      </article>

      <article class="panel chart-card wide">
        <div class="panel-head">
          <h2>推荐趋势</h2>
          <span>按天统计推荐请求与反馈</span>
        </div>
        <div ref="trendEl" class="chart-box"></div>
      </article>
    </section>

    <section class="bottom-grid">
      <article class="panel table-card">
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
            <tr v-for="row in selectionRows" :key="row.product_id">
              <td>{{ row.name }}</td>
              <td><span class="tag" :class="row.layer">{{ row.layer }}</span></td>
              <td>{{ formatNumber(row.selection_score) }}</td>
              <td>{{ row.effective_stock }}</td>
              <td>{{ formatPercent(row.ctr) }}</td>
              <td>{{ formatPercent(row.conversion_rate) }}</td>
            </tr>
          </tbody>
        </table>
      </article>

      <article class="panel table-card">
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
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in inventoryRows" :key="row.product_id">
              <td>{{ row.name }}</td>
              <td><span class="tag risk">{{ row.risk_level }}</span></td>
              <td>{{ row.available_stock }}</td>
              <td>{{ row.locked_stock }}</td>
              <td>{{ row.effective_stock }}</td>
            </tr>
          </tbody>
        </table>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { fetchFunnel, fetchInventory, fetchOverview, fetchProfiles, fetchSelection } from '../api/dashboard'
import type { DashboardFilters, FunnelData, InventoryHealthData, OverviewData, SelectionData, UserProfileData } from '../types/dashboard'

const STORAGE_KEY = 'ir_dashboard_demo_mode'
const demoMode = ref(localStorage.getItem(STORAGE_KEY) === 'true')
const filters = reactive<DashboardFilters>(createDefaultFilters())

const overview = ref<OverviewData | null>(null)
const funnel = ref<FunnelData | null>(null)
const selection = ref<SelectionData | null>(null)
const profiles = ref<UserProfileData | null>(null)
const inventory = ref<InventoryHealthData | null>(null)

const funnelEl = ref<HTMLDivElement | null>(null)
const layerEl = ref<HTMLDivElement | null>(null)
const stageEl = ref<HTMLDivElement | null>(null)
const trendEl = ref<HTMLDivElement | null>(null)
const gaugeEl = ref<HTMLDivElement | null>(null)

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

function setDemoLowStock() {
  demoMode.value = true
  localStorage.setItem(STORAGE_KEY, 'true')
  filters.scene = 'home'
  reloadAll()
}

function setDemoHealthy() {
  demoMode.value = true
  localStorage.setItem(STORAGE_KEY, 'true')
  filters.scene = ''
  reloadAll()
}

function setDemoHot() {
  demoMode.value = true
  localStorage.setItem(STORAGE_KEY, 'true')
  filters.scene = 'detail'
  reloadAll()
}

function setDemoRisk() {
  demoMode.value = true
  localStorage.setItem(STORAGE_KEY, 'true')
  filters.scene = 'cart'
  reloadAll()
}

function setDemoHomeScene() {
  filters.scene = 'home'
  reloadAll()
}

function setDemoDetailScene() {
  filters.scene = 'detail'
  reloadAll()
}

function setDemoCartScene() {
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
  const nextFilters = { ...filters }
  const [overviewData, funnelData, selectionData, profileData, inventoryData] = await Promise.all([
    fetchOverview(nextFilters),
    fetchFunnel(nextFilters),
    fetchSelection(nextFilters),
    fetchProfiles(nextFilters),
    fetchInventory(nextFilters),
  ])
  overview.value = overviewData
  funnel.value = funnelData
  selection.value = selectionData
  profiles.value = profileData
  inventory.value = inventoryData
  await nextTick()
  renderCharts()
}

function renderCharts() {
  renderGaugeChart()
  renderFunnelChart()
  renderLayerChart()
  renderStageChart()
  renderTrendChart()
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

onMounted(() => {
  reloadAll()
})
</script>
