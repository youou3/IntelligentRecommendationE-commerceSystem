export interface DashboardFilters {
  tenant_id: string
  merchant_id: string
  start_date: string
  end_date: string
  scene?: string
  request_id?: string
}

export interface DashboardResponse<T> {
  success: boolean
  code: string
  message: string
  request_id?: string | null
  data: T
}

export interface OverviewData {
  filters: DashboardFilters
  kpis: Record<string, number>
}

export interface FunnelData {
  summary: Record<string, number>
  funnel: Array<Record<string, unknown>>
  trend: Array<Record<string, unknown>>
  by_scene: Array<Record<string, unknown>>
}

export interface SelectionData {
  layer_distribution: Array<{ layer: string; count: number }>
  top_products: Array<Record<string, unknown>>
  risk_products: Array<Record<string, unknown>>
}

export interface UserProfileData {
  summary: Record<string, number>
  stage_distribution: Array<Record<string, unknown>>
  top_categories: Array<Record<string, unknown>>
  top_tags: Array<Record<string, unknown>>
  price_preference: Array<Record<string, unknown>>
}

export interface InventoryHealthData {
  summary: Record<string, number>
  stock_by_category: Array<Record<string, unknown>>
  risk_products: Array<Record<string, unknown>>
}
