import { apiClient } from './client'
import type {
  Notebook,
  Execution,
  ReproducibilityAnalysis,
  PackageResponse,
  DiffResponse,
} from '@/types'

export class NotebookService {
  // ==================== CRUD ====================

  async getAll(): Promise<Notebook[]> {
    const response = await apiClient.get<Notebook[]>('/notebooks/')
    return response.data
  }

  async getById(id: string | number): Promise<Notebook> {
    const response = await apiClient.get<Notebook>(`/notebooks/${id}/`)
    return response.data
  }

  async create(
    notebook: Omit<Notebook, 'id' | 'created_at' | 'updated_at' | 'author'>,
  ): Promise<Notebook> {
    const response = await apiClient.post<Notebook>('/notebooks/', notebook)
    return response.data
  }

  async update(id: string | number, notebook: Partial<Notebook>): Promise<Notebook> {
    const response = await apiClient.patch<Notebook>(`/notebooks/${id}/`, notebook)
    return response.data
  }

  async delete(id: string | number): Promise<void> {
    await apiClient.delete(`/notebooks/${id}/`)
  }

  // ==================== Execution ====================

  async execute(id: string | number): Promise<Execution> {
    const response = await apiClient.post<Execution>(`/notebooks/${id}/execute/`)
    return response.data
  }

  async getExecutions(notebookId: string | number): Promise<Execution[]> {
    const response = await apiClient.get<Execution[]>(`/notebooks/${notebookId}/executions/`)
    return response.data
  }

  async getExecutionById(
    notebookId: string | number,
    executionId: string | number,
  ): Promise<Execution> {
    const response = await apiClient.get<Execution>(
      `/notebooks/${notebookId}/executions/${executionId}/`,
    )
    return response.data
  }

  // ==================== Reproducibility ====================

  async getReproducibilityAnalysis(id: string | number): Promise<ReproducibilityAnalysis> {
    const response = await apiClient.get<ReproducibilityAnalysis>(
      `/notebooks/${id}/reproducibility/`,
    )
    return response.data
  }

  async generatePackage(id: string | number): Promise<PackageResponse> {
    const response = await apiClient.post<PackageResponse>(`/notebooks/${id}/generate_package/`)
    return response.data
  }

  async generateDiff(id: string | number, baseVersion?: string): Promise<DiffResponse> {
    const response = await apiClient.post<DiffResponse>(
      `/notebooks/${id}/generate_diff/`,
      baseVersion ? { base_version: baseVersion } : undefined,
    )
    return response.data
  }

  // ==================== Downloads ====================

  async download(id: string | number, format: 'rmd' | 'html' = 'rmd'): Promise<Blob> {
    const response = await apiClient.get<Blob>(`/notebooks/${id}/download/`, {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  }

  async downloadPackage(id: string | number): Promise<Blob> {
    const response = await apiClient.get<Blob>(`/notebooks/${id}/download_package/`, {
      responseType: 'blob',
    })
    return response.data
  }

  // ==================== Helpers ====================

  /**
   * Trigger download in browser
   */
  triggerDownload(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  /**
   * Download notebook and trigger browser download
   */
  async downloadAndSave(id: string | number, filename?: string): Promise<void> {
    const blob = await this.download(id)
    const defaultFilename = filename || `notebook_${id}.Rmd`
    this.triggerDownload(blob, defaultFilename)
  }

  /**
   * Download package and trigger browser download
   */
  async downloadPackageAndSave(id: string | number, filename?: string): Promise<void> {
    const blob = await this.downloadPackage(id)
    const defaultFilename = filename || `notebook_${id}_package.zip`
    this.triggerDownload(blob, defaultFilename)
  }
}

export const notebookService = new NotebookService()
