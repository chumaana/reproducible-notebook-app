import axios from 'axios'
import type { AxiosInstance } from 'axios'

// Type definitions
export interface Notebook {
  id?: string
  title: string
  content?: string
  author?: string
  created_at?: string
  updated_at?: string
  is_public?: boolean
  blocks?: NotebookBlock[]
}

export interface NotebookBlock {
  id?: string
  notebook?: string
  block_type: 'code' | 'markdown'
  content: string
  order: number
  output?: string
  created_at?: string
  updated_at?: string
  executing?: boolean
}

export interface ApiError {
  message: string
  status: number
}

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    })

    this.client.interceptors.request.use(
      (config) => {
        return config
      },
      (error) => Promise.reject(error),
    )

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject({
          message: error.response?.data?.message || error.message,
          status: error.response?.status || 500,
        } as ApiError)
      },
    )
  }

  // Notebook methods
  async getNotebooks(): Promise<Notebook[]> {
    const response = await this.client.get<Notebook[]>('/notebooks/')
    return response.data
  }

  async getNotebook(id: string): Promise<Notebook> {
    const response = await this.client.get<Notebook>(`/notebooks/${id}/`)
    return response.data
  }

  async createNotebook(notebook: Partial<Notebook>): Promise<Notebook> {
    const response = await this.client.post<Notebook>('/notebooks/', notebook)
    return response.data
  }

  async updateNotebook(id: string, notebook: Partial<Notebook>): Promise<Notebook> {
    const response = await this.client.patch<Notebook>(`/notebooks/${id}/`, notebook)
    return response.data
  }

  async deleteNotebook(id: string): Promise<void> {
    await this.client.delete(`/notebooks/${id}/`)
  }

  async executeNotebook(id: string): Promise<any> {
    const response = await this.client.post(`/notebooks/${id}/execute/`)
    return response.data
  }

  // Block methods
  async updateBlock(id: string, block: Partial<NotebookBlock>): Promise<NotebookBlock> {
    const response = await this.client.patch<NotebookBlock>(`/blocks/${id}/`, block)
    return response.data
  }

  async deleteBlock(id: string): Promise<void> {
    await this.client.delete(`/blocks/${id}/`)
  }
}

// Export singleton instance
export const api = new ApiService()
export default api
