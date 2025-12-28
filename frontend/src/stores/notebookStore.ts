import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sha256 } from 'js-sha256'
import api from '@/services/api'
import type { Notebook, AnalysisData, StaticAnalysisIssue } from '@/types'

export const useNotebookStore = defineStore('notebook', () => {
  // --- STATE ---
  const notebook = ref<Notebook>({ title: '', content: '' })
  const analysis = ref<AnalysisData | null>(null)
  const staticAnalysis = ref<any>(null)

  // The hash of the content at the moment the package was built
  const syncedContentHash = ref<string>('')

  // Flags
  const executing = ref(false)
  const packageGenerating = ref(false)
  const diffGenerating = ref(false)
  const packageLoading = ref(false) // State managed by store now

  // Results
  const executionResult = ref<string | null>(null)
  const executionError = ref<string | null>(null)
  const diffResult = ref<string | null>(null)

  // --- COMPUTED ---
  const currentHash = computed(() => sha256(notebook.value.content || ''))

  const hasExecuted = computed(() => !!executionResult.value && executionResult.value.length > 0)
  const hasPackage = computed(() => !!analysis.value?.dockerfile)

  // Package is up to date if we have a hash AND it matches current content
  const isPackageUpToDate = computed(() => {
    if (!syncedContentHash.value) return false
    return syncedContentHash.value === currentHash.value
  })

  const canDownloadPackage = computed(() => {
    // 1. If busy, no.
    if (packageGenerating.value || packageLoading.value) return false

    // 2. If no package exists on server, no.
    if (!hasPackage.value) return false

    // 3. If content has changed since last build, strict reproducibility says "No"
    // (User must rebuild to get a package that matches current code)
    if (!isPackageUpToDate.value) return false

    return true
  })

  const canGenerateDiff = computed(() => {
    return hasExecuted.value && hasPackage.value && !packageGenerating.value
  })

  const warnings = computed<StaticAnalysisIssue[]>(
    () => staticAnalysis.value?.issues || analysis.value?.static_analysis?.issues || [],
  )

  // --- ACTIONS ---

  function resetState() {
    notebook.value = { title: '', content: '' }
    analysis.value = null
    staticAnalysis.value = null
    syncedContentHash.value = ''
    executionResult.value = null
    executionError.value = null
    diffResult.value = null
    executing.value = false
    packageGenerating.value = false
  }

  async function load(id: string) {
    resetState()

    try {
      // 1. Load Notebook Basic Data
      notebook.value = await api.getNotebook(id)

      // 2. Load Execution History
      try {
        const executions = await api.getExecutions(Number(id))
        if (executions?.length > 0 && executions[0].status === 'completed') {
          executionResult.value = executions[0].html_output
        }
      } catch (e) {
        console.warn('Failed to load executions:', e)
      }

      // 3. Load Analysis (MAPPING LOGIC HERE)
      try {
        const rawData = await api.getAnalysis(Number(id))

        console.log('Raw DB Data:', rawData) // Debugging

        // --- MAP DATABASE FIELDS TO UI EXPECTATIONS ---
        analysis.value = {
          ...rawData,

          // UI expects 'manifest.system_packages'
          // DB has 'system_deps'
          manifest: {
            system_packages: rawData.system_deps || [],
          },

          // UI expects 'static_analysis.issues'
          // DB (via views.py) writes issues into 'dependencies'
          static_analysis: {
            issues: rawData.dependencies || [],
          },

          // Map the score if you want to use it
          score: rawData.r4r_score,
        }

        // Populate the warnings/issues list for the editor
        staticAnalysis.value = analysis.value.static_analysis

        // Initialize Hash for "Package Up To Date" check
        // If we have a Dockerfile OR system deps, we assume a package exists
        if (rawData.dockerfile || (rawData.system_deps && rawData.system_deps.length > 0)) {
          syncedContentHash.value = sha256(notebook.value.content || '')
        }
      } catch (e) {
        console.warn('Analysis not found (this is normal for new notebooks)', e)
      }
    } catch (e: any) {
      console.error('Critical error loading notebook:', e)
      notebook.value.title = 'Error loading notebook'
    }
  }
  async function save() {
    if (notebook.value.id) {
      await api.updateNotebook(notebook.value.id, notebook.value)
    } else {
      const created = await api.createNotebook(notebook.value)
      notebook.value = created
    }
  }

  async function runLocal() {
    if (!notebook.value.id) await save()
    executing.value = true
    executionError.value = null
    try {
      const res = await api.executeNotebook(notebook.value.id!)
      if (res.success) {
        executionResult.value = res.html || ''
        if (res.static_analysis) staticAnalysis.value = res.static_analysis
      } else {
        executionError.value = res.error || 'Execution failed'
      }
    } catch (e: any) {
      executionError.value = e.response?.data?.error || e.message
    } finally {
      executing.value = false
    }
  }

  async function runPackage() {
    if (!notebook.value.id) return
    packageGenerating.value = true
    executionError.value = null

    try {
      const res = await api.generatePackage(notebook.value.id)
      if (res.success) {
        // Sync the hash on success
        syncedContentHash.value = sha256(notebook.value.content || '')

        analysis.value = {
          ...analysis.value,
          dockerfile: res.dockerfile,
          makefile: res.makefile,
          manifest: res.manifest,
        }
      } else {
        executionError.value = res.error || 'Package failed'
      }
    } catch (e: any) {
      executionError.value = e.response?.data?.error || e.message
    } finally {
      packageGenerating.value = false
    }
  }

  async function runDiff() {
    if (!notebook.value.id) return
    diffGenerating.value = true
    executionError.value = null
    try {
      const res = await api.generateDiff(notebook.value.id)
      if (res.success) {
        diffResult.value = res.diff_html || ''
      } else {
        executionError.value = res.error || 'Diff failed'
      }
    } catch (e: any) {
      executionError.value = e.response?.data?.error || e.message
    } finally {
      diffGenerating.value = false
    }
  }

  // Moved Logic: Download
  async function downloadPackage() {
    if (!notebook.value.id || !hasPackage.value) return
    packageLoading.value = true
    try {
      const blob = await api.downloadPackage(notebook.value.id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `notebook_${notebook.value.id}_package.zip`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error(e)
      alert('Download failed')
    } finally {
      packageLoading.value = false
    }
  }

  return {
    notebook,
    analysis,
    staticAnalysis,
    warnings,
    executing,
    packageGenerating,
    diffGenerating,
    packageLoading,
    executionResult,
    executionError,
    diffResult,
    // Computed
    hasExecuted,
    hasPackage,
    canGenerateDiff,
    canDownloadPackage,
    isPackageUpToDate, // Exposed for UI tooltips
    // Actions
    load,
    save,
    runLocal,
    runPackage,
    runDiff,
    downloadPackage, // Exposed action
    resetState,
  }
})
