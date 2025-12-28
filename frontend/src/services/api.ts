import axios from 'axios'
import type {
  Notebook,
  ExecutionResponse,
  PackageResponse,
  DiffResponse,
  AnalysisData,
  Execution,
} from '@/types'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 600000,
})

const savedToken = localStorage.getItem('token')
if (savedToken) {
  api.defaults.headers.common['Authorization'] = `Token ${savedToken}`
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

export default {
  setToken(token: string) {
    api.defaults.headers.common['Authorization'] = `Token ${token}`
  },

  clearToken() {
    delete api.defaults.headers.common['Authorization']
  },

  async login(credentials: any) {
    const res = await api.post('/auth/login/', credentials)
    return res.data
  },

  async register(credentials: any) {
    const res = await api.post('/auth/register/', credentials)
    return res.data
  },
  async getUserProfile() {
    const res = await api.get('/auth/profile/')
    return res.data
  },

  async updateUserProfile(data: any) {
    const res = await api.patch('/auth/profile/', data)
    return res.data
  },

  async getNotebooks(): Promise<Notebook[]> {
    return (await api.get('/notebooks/')).data
  },

  async deleteNotebook(id: number): Promise<void> {
    await api.delete(`/notebooks/${id}/`)
  },

  // --- EDITOR METHODS ---
  async getNotebook(id: string | number): Promise<Notebook> {
    return (await api.get(`/notebooks/${id}/`)).data
  },

  async createNotebook(data: Notebook): Promise<Notebook> {
    return (await api.post('/notebooks/', data)).data
  },

  async updateNotebook(id: number, data: Notebook): Promise<Notebook> {
    return (await api.patch(`/notebooks/${id}/`, data)).data
  },

  // --- EXECUTION PIPELINE ---
  async executeNotebook(id: number): Promise<ExecutionResponse> {
    return (await api.post(`/notebooks/${id}/execute/`)).data
  },

  async generatePackage(id: number): Promise<PackageResponse> {
    return (await api.post(`/notebooks/${id}/generate_package/`)).data
  },

  async generateDiff(id: number): Promise<DiffResponse> {
    return (await api.post(`/notebooks/${id}/generate_diff/`)).data
  },

  // --- ANALYSIS & DOWNLOADS ---
  async getAnalysis(id: number): Promise<AnalysisData> {
    return (await api.get(`/notebooks/${id}/reproducibility/`)).data
  },

  async downloadPackage(id: number | string): Promise<void> {
    // 1. We must use responseType: 'blob' so axios doesn't try to parse ZIP as JSON
    const response = await api.get(`/notebooks/${id}/download_package/`, {
      responseType: 'blob',
    })

    // 2. Create a URL for the blob data
    const url = window.URL.createObjectURL(new Blob([response.data]))

    // 3. Create a temporary hidden link
    const link = document.createElement('a')
    link.href = url

    // 4. Set the filename (Backend usually provides this, or we set a default)
    link.setAttribute('download', `reproducibility_package_${id}.zip`)

    // 5. Append, click, and cleanup
    document.body.appendChild(link)
    link.click()

    // Cleanup to avoid memory leaks
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },
  async getExecutions(id: number): Promise<Execution[]> {
    return (await api.get(`/notebooks/${id}/executions/`)).data
  },
}
