export interface Notebook {
  id?: number
  title: string
  content: string
  author?: string
}

export interface StaticAnalysisIssue {
  code: string
  title: string
  severity: 'high' | 'medium' | 'low'
  details: string
  fix: string
  lines: { line_number: number; content: string }[]
}

export interface ExecutionResponse {
  success: boolean
  html?: string
  error?: string
  static_analysis?: {
    issues: StaticAnalysisIssue[]
    total_issues: number
  }
}

export interface PackageResponse {
  success: boolean
  dockerfile?: string
  makefile?: string
  manifest?: any
  error?: string
}

export interface DiffResponse {
  success: boolean
  diff_html?: string
  error?: string
}

export interface AnalysisData {
  dockerfile?: string
  makefile?: string
  manifest?: any
  detected_packages?: string[]
  static_analysis?: {
    issues: StaticAnalysisIssue[]
  }
}

export interface Execution {
  id: number
  status: string
  html_output: string
  created_at: string
}
