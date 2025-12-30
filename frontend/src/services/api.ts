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

  private initializeToken(): void {
    const token = localStorage.getItem('token')
    if (token) {
      this.setToken(token)
    }
  }

  public setToken(token: string): void {
    localStorage.setItem('token', token)
    this.api.defaults.headers.common['Authorization'] = `Token ${token}`
  }

  public clearToken(): void {
    localStorage.removeItem('token')
    delete this.api.defaults.headers.common['Authorization']
  }

  // Authentication
  async login(credentials: { username: string; password: string }) {
    const response = await this.api.post('/auth/login/', credentials)
    return response.data
  }

  async register(credentials: { username: string; email: string; password: string }) {
    const response = await this.api.post('/auth/register/', credentials)
    return response.data
  }

  async logout() {
    try {
      await this.api.post('/auth/logout/')
    } finally {
      this.clearToken()
      localStorage.removeItem('user')
    }
  }

  async getUserProfile() {
    const response = await this.api.get('/auth/profile/')
    return response.data
  }

  async updateUserProfile(data: Record<string, unknown>) {
    const response = await this.api.patch('/auth/profile/', data)
    return response.data
  }

  // Notebooks
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

  async getNotebook(id: string | number): Promise<Notebook> {
    const response = await this.api.get(`/notebooks/${id}/`)
    return response.data
  }

  async createNotebook(data: Partial<Notebook>): Promise<Notebook> {
    const response = await this.api.post('/notebooks/', data)
    return response.data
  }

  async updateNotebook(id: number, data: Partial<Notebook>): Promise<Notebook> {
    const response = await this.api.patch(`/notebooks/${id}/`, data)
    return response.data
  }

  async deleteNotebook(id: number): Promise<void> {
    await this.api.delete(`/notebooks/${id}/`)
  }

  /**
   * Toggle public/private status of a notebook
   * @param id Notebook ID
   * @returns Object with is_public status and message
   */
  async togglePublic(id: number): Promise<{ is_public: boolean; message: string }> {
    const response = await this.api.post(`/notebooks/${id}/toggle_public/`)
    return response.data
  }

  // Execution
  async executeNotebook(id: number): Promise<ExecutionResponse> {
    const response = await this.api.post(`/notebooks/${id}/execute/`)
    return response.data
  }

  async generatePackage(id: number): Promise<PackageResponse> {
    const response = await this.api.post(`/notebooks/${id}/generate_package/`)
    return response.data
  }

  async generateDiff(id: number): Promise<DiffResponse> {
    const response = await this.api.post(`/notebooks/${id}/generate_diff/`)
    return response.data
  }

  // Analysis
  async getAnalysis(id: number): Promise<AnalysisData> {
    const response = await this.api.get(`/notebooks/${id}/reproducibility/`)
    return response.data
  }

  /**
   * Download reproducibility package as ZIP file
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

  async getExecutions(id: number) {
    const response = await this.api.get(`/notebooks/${id}/executions/`)
    return response.data
  }
}

export default new ApiService()
