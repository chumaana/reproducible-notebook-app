import type { User } from './models.types'

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
  password_confirm?: string
}

export interface AuthResponse {
  token: string
  user: User
}

export interface ReproducibilityAnalysis {
  detected_packages?: string[]
  manifest?: Record<string, unknown>
  dockerfile?: string
  static_analysis?: {
    issues: Array<{
      type: string
      severity: 'high' | 'medium' | 'low'
      message: string
      line?: number
    }>
    total_issues: number
  }
}

export interface PackageResponse {
  package_path: string
  manifest: Record<string, unknown>
}

export interface DiffResponse {
  diff_html: string
}

export interface ApiError {
  message: string
  status?: number
  errors?: Record<string, string[]>
}

export interface ErrorResponse {
  error?: string
  detail?: string
  message?: string
  [key: string]: unknown
}

export interface HealthCheckResponse {
  status: string
  version?: string
}

export type UserProfile = User
