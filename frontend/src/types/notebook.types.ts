export interface Issue {
  type: string
  severity: 'high' | 'medium' | 'low'
  message: string
  lines: Array<{
    line_number: number
    code: string
  }>
}

export interface StaticAnalysis {
  issues: Issue[]
  total_issues: number
}

export interface ExecutionResult {
  success: boolean
  html?: string
  error?: string
  static_analysis?: StaticAnalysis
}

export interface PackageResult {
  success: boolean
  dockerfile?: string
  makefile?: string
  manifest?: Record<string, unknown>
  error?: string
}

export interface DiffResult {
  success: boolean
  diff_html?: string
  error?: string
}
