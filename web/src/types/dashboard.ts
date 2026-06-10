export interface DashboardFilters {
  tenant_id: string
  merchant_id: string
  start_date: string
  end_date: string
  scene?: string
  request_id?: string
  warning_level?: string
  status?: string
  category_id?: string
  page?: number
  page_size?: number
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

export interface InventoryWarningItem {
  id?: number
  product_id: string
  product_name?: string | null
  category_id?: string | null
  warning_level: string
  warning_reason: string[]
  status: string
  forecast_daily_sales: number
  stockout_days?: number | null
  suggested_action: string
  created_at?: string | null
  effective_stock?: number
  safe_stock?: number
  available_with_transit?: number
}

export interface InventoryWarningsData {
  request_id?: string
  run_id?: string
  page?: number
  page_size?: number
  total?: number
  items: InventoryWarningItem[]
}

export interface RunInventoryWarningsPayload {
  tenant_id: string
  merchant_id: string
  request_id: string
  product_ids?: string[]
  sales_days?: number
  persist?: boolean
}

export interface ReplenishmentSuggestPayload {
  tenant_id: string
  merchant_id: string
  request_id: string
  product_id: string
  forecast_days?: number
  warning_id?: number
  persist?: boolean
}

export interface ReplenishmentSuggestData {
  product_id: string
  forecast_days: number
  suggest_quantity: number
  target_stock: number
  effective_stock: number
  daily_sales: number
  action: string
  reason: string[]
  risk_note: string[]
  run_id: string
  replenishment_order_id?: number | null
  status: string
  selection_score?: number
  product_layer?: string
  warning_level?: string
}

export interface WorkflowRunView {
  workflow_name: string
  run_id: string
  request_id: string
  status: string
  summary: string
  created_at: string
}
