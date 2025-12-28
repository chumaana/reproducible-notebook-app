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

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

export default {
  // --- LIST VIEW METHODS (Додано) ---
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

  async downloadPackage(id: number): Promise<Blob> {
    return (await api.get(`/notebooks/${id}/download_package/`, { responseType: 'blob' })).data
  },
  async getExecutions(id: number): Promise<Execution[]> {
    return (await api.get(`/notebooks/${id}/executions/`)).data
  },
}
