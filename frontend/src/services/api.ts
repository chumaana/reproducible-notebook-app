import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type {
  Notebook,
  ExecutionResponse,
  PackageResponse,
  DiffResponse,
  AnalysisData,
} from '@/types/index'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const API_TIMEOUT = 600000

/**
 * API Service for communicating with Django backend
 * Handles authentication, notebook operations, and reproducibility features
 */
class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
    this.initializeToken()
  }

  /**
   * Configure axios request and response interceptors
   * - Adds authentication token to requests
   * - Handles 401 errors by clearing token and redirecting to login
   * @private
   */
  private setupInterceptors(): void {
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Token ${token}`
        }
        return config
      },
      (error) => Promise.reject(error),
    )

    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')

          const currentPath = window.location.pathname
          const isNotebookPath = currentPath.startsWith('/notebook/')

          if (!isNotebookPath && currentPath !== '/login') {
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      },
    )
  }

  /**
   * Initialize authentication token from localStorage if available
   * @private
   */
  private initializeToken(): void {
    const token = localStorage.getItem('token')
    if (token) {
      this.setToken(token)
    }
  }

  /**
   * Set authentication token and store in localStorage
   * @param token - Authentication token string
   * @public
   */
  public setToken(token: string): void {
    localStorage.setItem('token', token)
    this.api.defaults.headers.common['Authorization'] = `Token ${token}`
  }

  /**
   * Clear authentication token from storage and headers
   * @public
   */
  public clearToken(): void {
    localStorage.removeItem('token')
    delete this.api.defaults.headers.common['Authorization']
  }

  /**
   * Authenticate user with username and password
   * @param credentials - User credentials object
   * @param credentials.username - Username
   * @param credentials.password - Password
   * @returns Authentication response data including token
   */
  async login(credentials: { username: string; password: string }) {
    const response = await this.api.post('/auth/login/', credentials)
    return response.data
  }

  /**
   * Register a new user account
   * @param credentials - Registration credentials
   * @param credentials.username - Desired username
   * @param credentials.email - User email address
   * @param credentials.password - Password
   * @returns Registration response data
   */
  async register(credentials: { username: string; email: string; password: string }) {
    const response = await this.api.post('/auth/register/', credentials)
    return response.data
  }

  /**
   * Log out current user and clear authentication data
   * @returns Promise that resolves when logout is complete
   */
  async logout() {
    try {
      await this.api.post('/auth/logout/')
    } finally {
      this.clearToken()
      localStorage.removeItem('user')
    }
  }

  /**
   * Get current user's profile information
   * @returns User profile data
   */
  async getUserProfile() {
    const response = await this.api.get('/auth/profile/')
    return response.data
  }

  /**
   * Update current user's profile information
   * @param data - Profile data to update
   * @returns Updated profile data
   */
  async updateUserProfile(data: Record<string, unknown>) {
    const response = await this.api.patch('/auth/profile/', data)
    return response.data
  }

  /**
   * Get all notebooks accessible to the current user
   * @returns Array of notebooks
   */
  async getNotebooks(): Promise<Notebook[]> {
    const response = await this.api.get('/notebooks/')
    return response.data
  }

  /**
   * Get all public notebooks (no authentication required)
   * The backend automatically returns only public notebooks for unauthenticated users,
   * and returns user's notebooks + public notebooks for authenticated users.
   * @returns Array of accessible notebooks
   */
  async getPublicNotebooks(): Promise<Notebook[]> {
    const token = this.api.defaults.headers.common['Authorization']
    delete this.api.defaults.headers.common['Authorization']

    try {
      const response = await this.api.get('/notebooks/')
      return response.data
    } finally {
      if (token) {
        this.api.defaults.headers.common['Authorization'] = token
      }
    }
  }

  /**
   * Get a specific notebook by ID
   * @param id - Notebook ID (string or number)
   * @returns Notebook data
   */
  async getNotebook(id: string | number): Promise<Notebook> {
    const response = await this.api.get(`/notebooks/${id}/`)
    return response.data
  }

  /**
   * Create a new notebook
   * @param data - Partial notebook data for creation
   * @returns Created notebook data
   */
  async createNotebook(data: Partial<Notebook>): Promise<Notebook> {
    const response = await this.api.post('/notebooks/', data)
    return response.data
  }

  /**
   * Update an existing notebook
   * @param id - Notebook ID
   * @param data - Partial notebook data to update
   * @returns Updated notebook data
   */
  async updateNotebook(id: number, data: Partial<Notebook>): Promise<Notebook> {
    const response = await this.api.patch(`/notebooks/${id}/`, data)
    return response.data
  }

  /**
   * Delete a notebook
   * @param id - Notebook ID
   * @returns Promise that resolves when deletion is complete
   */
  async deleteNotebook(id: number): Promise<void> {
    await this.api.delete(`/notebooks/${id}/`)
  }

  /**
   * Toggle public/private status of a notebook
   * @param id - Notebook ID
   * @returns Object with is_public status and message
   */
  async togglePublic(id: number): Promise<{ is_public: boolean; message: string }> {
    const response = await this.api.post(`/notebooks/${id}/toggle_public/`)
    return response.data
  }

  /**
   * Execute a notebook and return execution results
   * @param id - Notebook ID
   * @returns Execution response data
   */
  async executeNotebook(id: number): Promise<ExecutionResponse> {
    const response = await this.api.post(`/notebooks/${id}/execute/`)
    return response.data
  }

  /**
   * Generate a reproducibility package for a notebook
   * @param id - Notebook ID
   * @returns Package generation response data
   */
  async generatePackage(id: number): Promise<PackageResponse> {
    const response = await this.api.post(`/notebooks/${id}/generate_package/`)
    return response.data
  }

  /**
   * Generate a diff comparison for a notebook
   * @param id - Notebook ID
   * @returns Diff generation response data
   */
  async generateDiff(id: number): Promise<DiffResponse> {
    const response = await this.api.post(`/notebooks/${id}/generate_diff/`)
    return response.data
  }

  /**
   * Get reproducibility analysis data for a notebook
   * @param id - Notebook ID
   * @returns Analysis data including reproducibility metrics
   */
  async getAnalysis(id: number): Promise<AnalysisData> {
    const response = await this.api.get(`/notebooks/${id}/reproducibility/`)
    return response.data
  }

  /**
   * Download reproducibility package as ZIP file
   * @param id - Notebook ID (string or number)
   * @returns Promise that resolves when download is initiated
   */
  async downloadPackage(id: number | string): Promise<void> {
    const response = await this.api.get(`/notebooks/${id}/download_package/`, {
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url

    const contentDisposition = response.headers['content-disposition']
    const filename = contentDisposition
      ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
      : `reproducibility_package_${id}.zip`

    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()

    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  /**
   * Download notebook as .Rmd file
   * @param id - Notebook ID (string or number)
   * @returns Promise that resolves when download is initiated
   */
  async downloadNotebook(id: number | string): Promise<void> {
    const response = await this.api.get(`/notebooks/${id}/download/`, {
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url

    const contentDisposition = response.headers['content-disposition']
    const filename = contentDisposition
      ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
      : `notebook_${id}.Rmd`

    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()

    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  /**
   * Get execution history for a notebook
   * @param id - Notebook ID
   * @returns Array of execution records
   */
  async getExecutions(id: number) {
    const response = await this.api.get(`/notebooks/${id}/executions/`)
    return response.data
  }
}

export default new ApiService()
