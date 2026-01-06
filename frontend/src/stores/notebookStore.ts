/**
 * Notebook Store
 * Manages notebook editing, execution, and reproducibility analysis
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getErrorMessage } from '@/utils/helpers'
import type { Notebook, AnalysisData, StaticAnalysisIssue, R4RData } from '@/types/index'

export const useNotebookStore = defineStore('notebook', () => {
  // State
  const notebook = ref<Notebook>({
    id: undefined,
    title: 'Untitled Notebook',
    content: '',
    author: '',
    is_public: false,
  })

  const executing = ref(false)
  const executionResult = ref<string | null>(null)
  const executionError = ref<string | null>(null)
  const packageGenerating = ref(false)
  const diffGenerating = ref(false)
  const packageLoading = ref(false)
  const analysis = ref<AnalysisData | null>(null)
  const diffResult = ref<string | null>(null)
  const staticAnalysis = ref<{ issues: StaticAnalysisIssue[] } | null>(null)
  const saveError = ref<string | null>(null)
  const r4rData = ref<R4RData | null>(null)

  // Computed
  const hasExecuted = computed(() => !!executionResult.value)
  const hasPackage = computed(() => !!analysis.value?.dockerfile)
  const canDownloadPackage = computed(() => hasPackage.value)
  const canGenerateDiff = computed(() => hasExecuted.value && hasPackage.value)
  const warnings = computed(() => staticAnalysis.value?.issues || [])
  const hasErrors = computed(() => !!executionError.value || !!saveError.value)
  const isLoading = computed(
    () =>
      executing.value || packageGenerating.value || diffGenerating.value || packageLoading.value,
  )

  // Actions
  /**
   * Reset all store state to initial values
   */
  function resetState() {
    notebook.value = {
      id: undefined,
      title: 'Untitled Notebook',
      content: '',
      author: '',
      is_public: false,
    }
    executionResult.value = null
    executionError.value = null
    saveError.value = null
    analysis.value = null
    diffResult.value = null
    staticAnalysis.value = null
    executing.value = false
    packageGenerating.value = false
    diffGenerating.value = false
    packageLoading.value = false
    r4rData.value = null
  }

  /**
   * Load notebook and its analysis data
   * @param id - Notebook ID to load
   */
  async function load(id: string): Promise<void> {
    // resetState()
    executionError.value = null

    try {
      // Load notebook data
      notebook.value = await api.getNotebook(id)

      // Load analysis data if available
      if (notebook.value.analysis) {
        analysis.value = notebook.value.analysis

        if (analysis.value.dependencies) {
          staticAnalysis.value = {
            issues: analysis.value.dependencies,
          }
        }

        if (analysis.value.diff_html) {
          diffResult.value = analysis.value.diff_html
        }

        if (analysis.value.r4r_data) {
          r4rData.value = analysis.value.r4r_data
        }
      }

      // Load execution history (optional, non-blocking)
      try {
        const executions = await api.getExecutions(Number(id))

        if (executions && executions.length > 0) {
          const lastExec = executions[0]
          if (lastExec && lastExec.status === 'completed') {
            executionResult.value = lastExec.html_output
            console.log(`Loaded execution result for notebook ${id}`)
          } else {
            console.log(`No completed executions found for notebook ${id}`)
          }
        } else {
          console.log(`No execution history for notebook ${id}`)
        }
      } catch (e) {
        const errorMsg = getErrorMessage(e)
        // Only log as warning since execution history is optional
        console.warn('Execution history unavailable:', errorMsg)

        // Check if it's an authentication error for a public notebook
        if (errorMsg.includes('Authentication') && notebook.value.is_public) {
          console.error(
            'BUG: Public notebook should not require authentication for execution history',
          )
        }
      }
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err)
      console.error('Failed to load notebook:', errorMsg)
      executionError.value = `Failed to load notebook: ${errorMsg}`
      throw err
    }
  }

  /**
   * Save notebook with title, content, and visibility status
   * @returns Notebook ID
   */
  async function save(): Promise<number | undefined> {
    saveError.value = null

    try {
      if (notebook.value.id) {
        // Update existing notebook
        const updated = await api.updateNotebook(notebook.value.id, {
          title: notebook.value.title,
          content: notebook.value.content,
          is_public: notebook.value.is_public,
        })
        notebook.value = { ...notebook.value, ...updated }
        return notebook.value.id
      } else {
        // Create new notebook
        const newNb = await api.createNotebook({
          title: notebook.value.title,
          content: notebook.value.content,
          is_public: notebook.value.is_public,
        })
        notebook.value = {
          ...notebook.value,
          id: newNb.id,
          author: newNb.author,
          is_public: newNb.is_public,
        }
        return newNb.id
      }
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err)
      console.error('Save failed:', errorMsg)
      saveError.value = errorMsg
      throw err
    }
  }

  /**
   * Execute notebook locally and run static analysis
   */
  async function runLocal(): Promise<void> {
    if (!notebook.value.id) {
      executionError.value = 'Cannot execute: notebook not saved'
      return
    }

    executing.value = true
    executionError.value = null

    try {
      await save()
      const res = await api.executeNotebook(notebook.value.id)

      if (res.success) {
        executionResult.value = res.html ?? null

        if (res.static_analysis?.issues) {
          staticAnalysis.value = {
            issues: res.static_analysis.issues,
          }
        }
      } else {
        executionError.value = res.error || 'Execution failed'
      }
    } catch (err: unknown) {
      executionError.value = getErrorMessage(err)
    } finally {
      executing.value = false
    }
  }

  /**
   * Generate reproducibility package with R4R
   */
  async function runPackage(): Promise<void> {
    if (!notebook.value.id) {
      console.error('Cannot generate package: notebook not saved')
      return
    }

    packageGenerating.value = true

    try {
      const res = await api.generatePackage(notebook.value.id)

      if (res.success) {
        if (!analysis.value) {
          analysis.value = {}
        }

        if (res.r4r_data) {
          r4rData.value = res.r4r_data
        }

        analysis.value.dockerfile = res.dockerfile
        analysis.value.makefile = res.makefile

        if (res.manifest?.system_packages) {
          analysis.value.system_deps = res.manifest.system_packages
        }
      }
    } catch (err: unknown) {
      console.error('Package generation failed:', getErrorMessage(err))
      throw err
    } finally {
      packageGenerating.value = false
    }
  }

  /**
   * Generate semantic diff between local and container execution
   */
  async function runDiff(): Promise<void> {
    if (!notebook.value.id) {
      console.error('Cannot generate diff: notebook not saved')
      return
    }

    diffGenerating.value = true
    diffResult.value = null

    try {
      const res = await api.generateDiff(notebook.value.id)

      if (res.success) {
        diffResult.value = res.diff_html || res.html || null
      }
    } catch (err: unknown) {
      console.error('Diff generation failed:', getErrorMessage(err))
      throw err
    } finally {
      diffGenerating.value = false
    }
  }

  /**
   * Download reproducibility package as ZIP file
   */
  async function downloadPackage(): Promise<void> {
    if (!notebook.value.id) {
      console.error('Cannot download: notebook not saved')
      return
    }

    packageLoading.value = true

    try {
      await api.downloadPackage(notebook.value.id)
    } catch (err: unknown) {
      console.error('Download failed:', getErrorMessage(err))
      throw err
    } finally {
      packageLoading.value = false
    }
  }

  /**
   * Clear all error messages
   */
  function clearErrors(): void {
    executionError.value = null
    saveError.value = null
  }

  return {
    // State
    notebook,
    executing,
    executionResult,
    executionError,
    saveError,
    packageGenerating,
    diffGenerating,
    packageLoading,
    analysis,
    staticAnalysis,
    diffResult,
    r4rData,
    // Computed
    hasExecuted,
    hasPackage,
    canDownloadPackage,
    canGenerateDiff,
    warnings,
    hasErrors,
    isLoading,
    // Actions
    load,
    save,
    resetState,
    runLocal,
    runPackage,
    runDiff,
    downloadPackage,
    clearErrors,
  }
})
