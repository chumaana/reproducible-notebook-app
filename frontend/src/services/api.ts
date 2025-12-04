import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
  id: number
  notebook: number
  r4r_score: number
  dependencies: string[]
  system_deps: string[]
  dockerfile: string
  makefile: string
  created_at: string
  updated_at: string
}

export default {
  // Notebooks
  async getNotebooks(): Promise<Notebook[]> {
    const response = await api.get('/notebooks/')
    return response.data
  },

  async getNotebook(id: string): Promise<Notebook> {
    const response = await api.get(`/notebooks/${id}/`)
    return response.data
  },

  async createNotebook(notebook: Notebook): Promise<Notebook> {
    const response = await api.post('/notebooks/', notebook)
    return response.data
  },

  async updateNotebook(id: number, notebook: Notebook): Promise<Notebook> {
    const response = await api.put(`/notebooks/${id}/`, notebook)
    return response.data
  },

  async deleteNotebook(id: string): Promise<void> {
    await api.delete(`/notebooks/${id}/`)
  },

  // Execution
  async executeNotebook(id: number): Promise<any> {
    const response = await api.post(`/notebooks/${id}/execute/`)
    return response.data
  },

  async getExecutions(notebookId: number): Promise<Execution[]> {
    const response = await api.get(`/notebooks/${notebookId}/executions/`)
    return response.data
  },

  // Reproducibility Analysis
  async getReproducibilityAnalysis(notebookId: number): Promise<ReproducibilityAnalysis> {
    const response = await api.get(`/notebooks/${notebookId}/reproducibility/`)
    return response.data
  },

  // Download
  async downloadNotebook(id: number): Promise<Blob> {
    const response = await api.get(`/notebooks/${id}/download/`, {
      responseType: 'blob',
    })
    return response.data
  },
}
