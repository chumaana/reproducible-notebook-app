import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getErrorMessage } from '@/utils/helpers'
import type { Notebook, AnalysisData, StaticAnalysisIssue, R4RData } from '@/types/index'

export const useNotebookStore = defineStore('notebook', () => {
  // ==================== STATE ====================
  const notebook = ref<Notebook>({
    id: undefined,
    title: 'Untitled Notebook',
    content: '',
    author: '',
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

  // ==================== COMPUTED ====================
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

  // ==================== ACTIONS ====================

  /**
   * Reset all state to initial values
   */
  function resetState() {
    notebook.value = {
      id: undefined,
      title: 'Untitled Notebook',
      content: '',
      author: '',
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
   * Load notebook by ID
   */
  async function load(id: string): Promise<void> {
    resetState()
    executionError.value = null

    try {
      // Load notebook data (includes nested analysis from backend)
      notebook.value = await api.getNotebook(id)

      // If notebook has analysis nested, extract it
      if (notebook.value.analysis) {
        analysis.value = notebook.value.analysis

        // Extract static analysis issues from dependencies field
        if (analysis.value.dependencies) {
          staticAnalysis.value = {
            issues: analysis.value.dependencies,
          }
        }

        // If diff_html exists, set it
        if (analysis.value.diff_html) {
          diffResult.value = analysis.value.diff_html
        }
        if (analysis.value.r4r_data) {
          r4rData.value = analysis.value.r4r_data
        }
      }

      // Load execution history (non-critical)
      try {
        const executions = await api.getExecutions(Number(id))
        if (executions.length > 0) {
          const lastExec = executions[0]
          if (lastExec.status === 'completed') {
            executionResult.value = lastExec.html_output
          }
        }
      } catch (e) {
        console.warn('Execution history unavailable:', getErrorMessage(e))
      }
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err)
      console.error('Failed to load notebook:', errorMsg)
      executionError.value = `Failed to load notebook: ${errorMsg}`
      throw err
    }
  }

  /**
   * Save current notebook
   */
  async function save(): Promise<number | undefined> {
    saveError.value = null

    try {
      if (notebook.value.id) {
        // Update existing notebook
        await api.updateNotebook(notebook.value.id, {
          title: notebook.value.title,
          content: notebook.value.content,
        })
        return notebook.value.id
      } else {
        // Create new notebook
        const newNb = await api.createNotebook({
          title: notebook.value.title,
          content: notebook.value.content,
        })
        notebook.value.id = newNb.id
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
   * Execute notebook locally
   */
  async function runLocal(): Promise<void> {
    if (!notebook.value.id) {
      executionError.value = 'Cannot execute: notebook not saved'
      return
    }

    executing.value = true
    executionError.value = null

    try {
      // Save before executing
      await save()

      const res = await api.executeNotebook(notebook.value.id)

      if (res.success) {
        executionResult.value = res.html ?? null

        // Backend saves static analysis to ReproducibilityAnalysis.dependencies
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
   * Generate reproducibility package
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
        // Update local analysis state
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
        console.log('kjhbjhbhb')
        alert('Package has been generated!\n')
      }
    } catch (err: unknown) {
      console.error('Package generation failed:', getErrorMessage(err))
      throw err
    } finally {
      packageGenerating.value = false
    }
  }

  /**
   * Generate diff between original and executed
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
        // Backend returns diff_html or html
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
   * Download reproducibility package as ZIP
   */
  async function downloadPackage(): Promise<void> {
    if (!notebook.value.id) {
      console.error('Cannot download: notebook not saved')
      return
    }

    packageLoading.value = true

    try {
      console.log('Downloading package for notebook:', notebook.value.id)
      await api.downloadPackage(notebook.value.id)
      console.log('Download completed successfully')
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

  // ==================== RETURN ====================
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
