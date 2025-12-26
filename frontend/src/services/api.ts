import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    console.log('🔑 Token exists:', !!token) // Debug
    console.log('🔑 Token value:', token) // Debug
    if (token) {
      config.headers.Authorization = `Token ${token}`
      console.log(
        '✅ Authorization header:',
        config.headers.Authorization?.substring(0, 30) + '...',
      ) // Debug
    } else {
      console.log('❌ No token found!')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

export interface Notebook {
  id?: number
  title: string
  content: string
  author?: string
  created_at?: string
  updated_at?: string
  is_public?: boolean
}

export interface Execution {
  id: number
  notebook: number
  html_output: string
  status: string
  started_at: string
  completed_at?: string
  error_message?: string
}
export interface ReproducibilityAnalysis {
  detected_packages?: string[]
  manifest?: any
  dockerfile?: string
  static_analysis?: {
    issues: any[]
    total_issues: number
  }
}

export interface LoginPayload {
  username?: string
  email?: string
  password?: string
}

export interface RegisterPayload {
  username: string
  email?: string
  password?: string
  password_confirm?: string
}

export default {
  async login(credentials: LoginPayload) {
    const response = await api.post('/auth/login/', credentials)
    return response.data
  },
  async register(credentials: RegisterPayload) {
    const response = await api.post('/auth/register/', credentials)
    return response.data
  },

  async logout() {
    const response = await api.post('/auth/logout/')
    return response.data
  },

  async getUser() {
    const response = await api.get('/auth/user/')
    return response.data
  },

  async getNotebooks(): Promise<Notebook[]> {
    const response = await api.get('/notebooks/')
    return response.data
  },

  async getNotebook(id: string | number): Promise<Notebook> {
    const response = await api.get(`/notebooks/${id}/`)
    return response.data
  },

  async createNotebook(notebook: Notebook): Promise<Notebook> {
    const response = await api.post('/notebooks/', notebook)
    return response.data
  },

  async updateNotebook(id: number, notebook: Notebook): Promise<Notebook> {
    const response = await api.patch(`/notebooks/${id}/`, notebook)
    return response.data
  },

  async deleteNotebook(id: string | number): Promise<void> {
    await api.delete(`/notebooks/${id}/`)
  },

  async executeNotebook(id: number): Promise<any> {
    const response = await api.post(`/notebooks/${id}/execute/`)
    return response.data
  },

  async getExecutions(notebookId: number): Promise<Execution[]> {
    const response = await api.get(`/notebooks/${notebookId}/executions/`)
    return response.data
  },

  async getReproducibilityAnalysis(notebookId: number): Promise<ReproducibilityAnalysis> {
    const response = await api.get(`/notebooks/${notebookId}/reproducibility/`)
    return response.data
  },

  async downloadNotebook(id: number): Promise<Blob> {
    const response = await api.get(`/notebooks/${id}/download/`, {
      responseType: 'blob',
    })
    return response.data
  },

  async downloadPackage(id: number): Promise<Blob> {
    const response = await api.get(`/notebooks/${id}/download_package/`, {
      responseType: 'blob',
    })
    return response.data
  },
  async getUserProfile() {
    const response = await api.get('/profile/')
    return response.data
  },

  async updateUserProfile(data: any) {
    const response = await api.patch('/profile/', data)
    return response.data
  },
}
