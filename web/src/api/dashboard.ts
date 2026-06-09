import { request } from './client'
import type {
  DashboardFilters,
  FunnelData,
  InventoryHealthData,
  OverviewData,
  SelectionData,
  UserProfileData,
} from '../types/dashboard'

function toQuery(filters: Partial<DashboardFilters>) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.set(key, String(value))
    }
  })
  return params.toString()
}

const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

const baseFilters = (filters: Partial<DashboardFilters>): DashboardFilters => ({
  tenant_id: filters.tenant_id || 'T1',
  merchant_id: filters.merchant_id || 'M1',
  start_date: filters.start_date || getDefaultStartDate(),
  end_date: filters.end_date || getDefaultEndDate(),
  scene: filters.scene || '',
  request_id: filters.request_id || 'REQ-DEMO',
})

function getDefaultEndDate() {
  return new Date().toISOString().slice(0, 10)
}

function getDefaultStartDate() {
  const d = new Date()
  d.setDate(d.getDate() - 6)
  return d.toISOString().slice(0, 10)
}

function buildDemoOverview(filters: Partial<DashboardFilters>): OverviewData {
  const merged = baseFilters(filters)
  return {
    filters: merged,
    kpis: {
      behavior_events: 128,
      recommendation_requests: 32,
      exposures: 96,
      clicks: 22,
      add_carts: 9,
      conversions: 4,
      ctr: 0.2292,
      add_cart_rate: 0.0938,
      conversion_rate: 0.0417,
      active_products: 56,
      low_stock_products: 6,
      profiled_users: 24,
    },
  }
}

function buildDemoFunnel(): FunnelData {
  return {
    summary: {
      recommendation_requests: 32,
      exposures: 96,
      clicks: 22,
      add_carts: 9,
      conversions: 4,
      ctr: 0.2292,
      add_cart_rate: 0.0938,
      conversion_rate: 0.0417,
    },
    funnel: [
      { stage: 'exposure', label: '曝光', count: 96, rate_from_previous: 1 },
      { stage: 'click', label: '点击', count: 22, rate_from_previous: 0.2292 },
      { stage: 'add_cart', label: '加购', count: 9, rate_from_previous: 0.4091 },
      { stage: 'convert', label: '转化', count: 4, rate_from_previous: 0.4444 },
    ],
    trend: Array.from({ length: 7 }).map((_, idx) => ({
      date: `06-${String(idx + 1).padStart(2, '0')}`,
      recommendation_requests: 4 + idx,
      exposures: 12 + idx * 2,
      clicks: 3 + idx,
      add_carts: 1 + (idx % 3),
      conversions: idx % 2,
    })),
    by_scene: [
      { scene: 'home', exposures: 60, clicks: 14, add_carts: 6, conversions: 3, ctr: 0.2333, conversion_rate: 0.05 },
      { scene: 'detail', exposures: 36, clicks: 8, add_carts: 3, conversions: 1, ctr: 0.2222, conversion_rate: 0.0278 },
    ],
  }
}

function buildDemoSelection(): SelectionData {
  return {
    layer_distribution: [
      { layer: 'hot', count: 4 },
      { layer: 'potential', count: 6 },
      { layer: 'long_tail', count: 10 },
      { layer: 'risk', count: 3 },
    ],
    top_products: [
      {
        product_id: 'P10001',
        name: 'Running Shoes',
        category_id: 'C10001',
        selection_score: 0.92,
        layer: 'hot',
        effective_stock: 18,
        safe_stock: 5,
        exposures: 100,
        clicks: 24,
        add_carts: 10,
        conversions: 5,
        ctr: 0.24,
        conversion_rate: 0.05,
      },
      {
        product_id: 'P10002',
        name: 'Summer Tee',
        category_id: 'C10002',
        selection_score: 0.71,
        layer: 'potential',
        effective_stock: 9,
        safe_stock: 8,
        exposures: 66,
        clicks: 12,
        add_carts: 4,
        conversions: 2,
        ctr: 0.1818,
        conversion_rate: 0.0303,
      },
    ],
    risk_products: [
      {
        product_id: 'P10009',
        name: 'Winter Jacket',
        category_id: 'C10009',
        selection_score: 0.22,
        layer: 'risk',
        risk_type: 'low_stock',
        effective_stock: 0,
        safe_stock: 5,
      },
    ],
  }
}

function buildDemoProfiles(): UserProfileData {
  return {
    summary: {
      profiled_users: 24,
      active_behavior_users: 41,
      profile_coverage: 0.5854,
    },
    stage_distribution: [
      { user_stage: 'new', count: 10 },
      { user_stage: 'active_browsing', count: 8 },
      { user_stage: 'strong_intent', count: 5 },
      { user_stage: 'converted', count: 1 },
    ],
    top_categories: [
      { category_id: 'C10001', weight: 18.5, user_count: 12 },
      { category_id: 'C10002', weight: 15.2, user_count: 9 },
      { category_id: 'C10003', weight: 11.1, user_count: 7 },
    ],
    top_tags: [
      { tag: 'running', weight: 22.0, user_count: 15 },
      { tag: 'summer', weight: 16.5, user_count: 12 },
      { tag: 'lightweight', weight: 13.2, user_count: 8 },
    ],
    price_preference: [
      { bucket: 'low', count: 7 },
      { bucket: 'middle', count: 11 },
      { bucket: 'high', count: 6 },
    ],
  }
}

function buildDemoInventory(): InventoryHealthData {
  return {
    summary: {
      total_products: 60,
      active_products: 54,
      inactive_products: 6,
      low_stock_products: 6,
      out_of_stock_products: 2,
      healthy_products: 52,
    },
    stock_by_category: [
      { category_id: 'C10001', product_count: 12, effective_stock: 180, low_stock_products: 1, out_of_stock_products: 0 },
      { category_id: 'C10002', product_count: 8, effective_stock: 86, low_stock_products: 2, out_of_stock_products: 1 },
      { category_id: 'C10003', product_count: 9, effective_stock: 120, low_stock_products: 0, out_of_stock_products: 0 },
    ],
    risk_products: [
      {
        product_id: 'P10009',
        name: 'Winter Jacket',
        category_id: 'C10009',
        status: 'active',
        available_stock: 0,
        locked_stock: 0,
        effective_stock: 0,
        safe_stock: 5,
        risk_level: 'out_of_stock',
      },
      {
        product_id: 'P10010',
        name: 'Sport Socks',
        category_id: 'C10010',
        status: 'active',
        available_stock: 4,
        locked_stock: 2,
        effective_stock: 2,
        safe_stock: 5,
        risk_level: 'low_stock',
      },
    ],
  }
}

export async function fetchOverview(filters: Partial<DashboardFilters>) {
  if (DEMO_MODE) return buildDemoOverview(filters)
  return request<OverviewData>(`/api/dashboard/overview?${toQuery(filters)}`)
}

export async function fetchFunnel(filters: Partial<DashboardFilters>) {
  if (DEMO_MODE) return buildDemoFunnel()
  return request<FunnelData>(`/api/dashboard/recommendation-funnel?${toQuery(filters)}`)
}

export async function fetchSelection(filters: Partial<DashboardFilters>) {
  if (DEMO_MODE) return buildDemoSelection()
  return request<SelectionData>(`/api/dashboard/product-selection?${toQuery(filters)}`)
}

export async function fetchProfiles(filters: Partial<DashboardFilters>) {
  if (DEMO_MODE) return buildDemoProfiles()
  return request<UserProfileData>(`/api/dashboard/user-profiles?${toQuery(filters)}`)
}

export async function fetchInventory(filters: Partial<DashboardFilters>) {
  if (DEMO_MODE) return buildDemoInventory()
  return request<InventoryHealthData>(`/api/dashboard/inventory-health?${toQuery(filters)}`)
}
