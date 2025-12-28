// ==================== USER & AUTH ====================
export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  date_joined?: string
  notebook_count?: number
}

export interface AuthResponse {
  token: string
  user: User
}

// ==================== NOTEBOOK ====================
export interface Notebook {
  id?: number
  title: string
  content: string
  author?: string
  author_id?: number
  created_at?: string
  updated_at?: string
  is_public?: boolean
  analysis?: AnalysisData
  execution_count?: number
  last_execution_status?: string
  has_analysis?: boolean
}

// ==================== EXECUTION ====================
export interface Execution {
  id: number
  notebook: number
  notebook_title?: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  html_output: string
  error_message?: string
  duration_seconds?: number | null
  started_at: string
  completed_at?: string | null
}

export interface ExecutionResponse {
  success: boolean
  html?: string
  error?: string
  static_analysis?: {
    issues: StaticAnalysisIssue[]
    total_issues?: number
  }
  r4r_data?: R4RData
}

// ==================== STATIC ANALYSIS ====================
export interface StaticAnalysisIssue {
  code: string
  title: string
  severity: 'high' | 'medium' | 'low'
  details: string
  fix: string
  lines: { line_number: number; code: string }[]
}

// ==================== REPRODUCIBILITY ANALYSIS ====================
export interface AnalysisData {
  id?: number
  notebook?: number
  notebook_title?: string
  dependencies?: StaticAnalysisIssue[]
  system_deps?: string[]
  dockerfile?: string
  makefile?: string
  diff_html?: string | null
  created_at?: string
  updated_at?: string
  r4r_data?: R4RData
}

// ==================== R4R REPRODUCIBILITY ====================
export interface R4RData {
  r_packages: string[]
  system_libs: string[]
  files_accessed: number
  image_size_mb?: number
  reproducibility_score?: number
  cache_hit?: boolean
}

// ==================== PACKAGE & DIFF ====================
export interface PackageResponse {
  success: boolean
  dockerfile?: string
  makefile?: string
  manifest?: {
    system_packages: string[]
  }
  error?: string
  r4r_data?: R4RData
  build_success?: boolean
  duration_seconds?: number
  package_ready?: boolean
}

export interface DiffResponse {
  success: boolean
  diff_html?: string
  html?: string
  error?: string
}
