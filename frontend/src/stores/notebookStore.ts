import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import axios from 'axios'
import type { Notebook, AnalysisData, StaticAnalysisIssue } from '@/types/types'

export const useNotebookStore = defineStore('notebook', () => {
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

  function getErrorMessage(err: unknown): string {
    if (axios.isAxiosError(err)) {
      return err.response?.data?.error || err.message
    }
    if (err instanceof Error) return err.message
    return String(err)
  }

  // === COMPUTED ===
  const hasExecuted = computed(() => !!executionResult.value)
  const hasPackage = computed(() => !!analysis.value?.dockerfile)
  const canDownloadPackage = computed(() => hasPackage.value)
  const canGenerateDiff = computed(() => hasExecuted.value && hasPackage.value)
  const warnings = computed(() => staticAnalysis.value?.issues || [])

  // === ACTIONS ===
  function resetState() {
    notebook.value = { title: 'Untitled Notebook', content: '' }
    executionResult.value = null
    executionError.value = null
    analysis.value = null
    diffResult.value = null
    staticAnalysis.value = null
    executing.value = false
    packageGenerating.value = false
    diffGenerating.value = false
    packageLoading.value = false
  }

  async function load(id: string) {
    resetState()
    try {
      notebook.value = await api.getNotebook(id)

      try {
        const executions = await api.getExecutions(Number(id))
        if (executions.length > 0) {
          const lastExec = executions[0]
          if (lastExec.status === 'completed') {
            executionResult.value = lastExec.html_output
          }
        }
      } catch (e) {
        console.warn('Execution history fetch skipped/failed:', getErrorMessage(e))
      }

      try {
        const rawData = await api.getAnalysis(Number(id))
        analysis.value = {
          ...rawData,
          manifest: { system_packages: rawData.system_deps || [] },
          static_analysis: { issues: rawData.dependencies || [] },
        }

        if (analysis.value.static_analysis) {
          staticAnalysis.value = analysis.value.static_analysis
        }

        if (rawData.diff_html) {
          diffResult.value = rawData.diff_html
        }
      } catch (e) {
        console.warn('Analysis data fetch skipped/failed:', getErrorMessage(e))
      }
    } catch (err: unknown) {
      console.error('Critical load failure:', err)
      executionError.value = `Failed to load notebook: ${getErrorMessage(err)}`
    }
  }

  async function save() {
    try {
      if (notebook.value.id) {
        await api.updateNotebook(notebook.value.id, {
          title: notebook.value.title,
          content: notebook.value.content,
        })
      } else {
        const newNb = await api.createNotebook({
          title: notebook.value.title,
          content: notebook.value.content,
        })

        notebook.value.id = newNb.id
        return newNb.id
      }
    } catch (err: unknown) {
      console.error('Save failed:', err)
    }
  }
  async function runLocal() {
    if (!notebook.value.id) return
    executing.value = true
    executionError.value = null

    try {
      await save()
      const res = await api.executeNotebook(notebook.value.id)

      if (res.success) {
        executionResult.value = res.html ?? null
        if (res.static_analysis?.issues) {
          staticAnalysis.value = { issues: res.static_analysis.issues }
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

  async function runPackage() {
    if (!notebook.value.id) return
    packageGenerating.value = true
    try {
      const res = await api.generatePackage(notebook.value.id)
      if (res.success && analysis.value) {
        analysis.value.dockerfile = res.dockerfile
        analysis.value.makefile = res.makefile
        if (res.manifest?.system_packages) {
          analysis.value.manifest = { system_packages: res.manifest.system_packages }
        }
      }
    } catch (err: unknown) {
      console.error('Package generation failed:', getErrorMessage(err))
    } finally {
      packageGenerating.value = false
    }
  }

  async function runDiff() {
    if (!notebook.value.id) return
    diffGenerating.value = true
    diffResult.value = null
    try {
      const res = await api.generateDiff(notebook.value.id)
      if (res.success) {
        diffResult.value = res.diff_html || res.html || null
      }
    } catch (err: unknown) {
      console.error('Diff failed:', getErrorMessage(err))
    } finally {
      diffGenerating.value = false
    }
  }

  async function downloadPackage() {
    if (!notebook.value.id) return

    packageLoading.value = true
    try {
      console.log('Triggering download for notebook:', notebook.value.id)
      await api.downloadPackage(notebook.value.id)
      console.log('Download request finished successfully')
    } catch (err: unknown) {
      console.error('Download failed:', err)
    } finally {
      packageLoading.value = false
    }
  }
  return {
    notebook,
    executing,
    executionResult,
    executionError,
    packageGenerating,
    diffGenerating,
    packageLoading,
    analysis,
    staticAnalysis,
    diffResult,
    hasExecuted,
    hasPackage,
    canDownloadPackage,
    canGenerateDiff,
    warnings,
    load,
    save,
    resetState,
    runLocal,
    runPackage,
    runDiff,
    downloadPackage,
  }
})
