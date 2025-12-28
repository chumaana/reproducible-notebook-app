// ==================== Common Types ====================
export type Severity = 'high' | 'medium' | 'low'
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed'

// ==================== Pagination ====================
export interface PaginationParams {
  page: number
  page_size: number
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ==================== Date/Time ====================
export interface DateRange {
  start: Date
  end: Date
}

// ==================== Generic Response ====================
export interface SuccessResponse {
  success: true
  message?: string
}

export interface ErrorResponseBase {
  success: false
  error: string
}
