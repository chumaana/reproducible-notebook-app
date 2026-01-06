<script setup lang="ts">
/**
 * NotebookEditor Component.
 * * The central integration point of the application. It orchestrates the lifecycle 
 * of an R Notebook: authoring, execution, dependency tracing (R4R), 
 * containerization (Docker), and reproducibility validation (RDiff).
 * * Key Features:
 * - Split-pane interface with synchronized R script editing and HTML preview.
 * - Reactive state management via Pinia (NotebookStore).
 * - Automatic conversion between raw R code and R Markdown format.
 * - Multi-stage pipeline: Local Run -> Package Generation -> Docker Diff -> Export.
 * - Permission-based UI: Toggles between Author (Edit) and Guest (Read-only) modes.
 */

import { ref, watch, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useNotebookStore } from '@/stores/notebookStore'
import { useMarkdown } from '@/composables/useMarkdown'

import EditorToolbar from '@/components/editor/EditorToolbar.vue'
import OutputPane from '@/components/editor/OutputPane.vue'
import AnalysisDrawer from '@/components/analysis/AnalysisDrawer.vue'
import DiffModal from '@/components/analysis/DiffModal.vue'
import router from '../router'

const route = useRoute()
const store = useNotebookStore()

/** * Store State Extraction.
 * Using storeToRefs to maintain reactivity when destructuring the Pinia store.
 */
const {
    notebook,
    executing,
    executionResult,
    executionError,
    packageGenerating,
    diffGenerating,
    packageLoading,
    hasExecuted,
    hasPackage,
    canGenerateDiff,
    canDownloadPackage,
    warnings,
    analysis,
    diffResult,
    staticAnalysis,
    r4rData,
} = storeToRefs(store)

// Local UI state
const notebookTitle = ref('Untitled Notebook')
const cleanContent = ref('')
const isPublic = ref(false)
const showAnalysis = ref(false)
const showDiffModal = ref(false)
const paneWidth = ref(600)
const placeholderText = `# Write your R code here...`

/** * Composable for R Markdown Transformations.
 * Logic encapsulated in useMarkdown converts raw editor text into a valid .Rmd 
 * file with YAML headers and code fences.
 */
const { extractCleanContent, generateFullRmd } = useMarkdown(notebookTitle, cleanContent)

/**
 * Component Lifecycle: Initialization.
 * Fetches existing notebooks based on URL parameters or initializes a fresh 
 * state for new notebooks.
 */
onMounted(async () => {
    const id = route.params.id as string
    if (id && id !== 'new') {
        await store.load(id)
    } else {
        store.resetState()
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        store.notebook.author = currentUser.username || ''
    }

    // Map store state to local reactive refs
    notebookTitle.value = store.notebook.title || 'Untitled Notebook'
    cleanContent.value = extractCleanContent(store.notebook.content)
    isPublic.value = store.notebook.is_public || false
})

/**
 * Persistence Logic: Auto-save.
 * Uses a debounced function to trigger a server-side save after 2 seconds 
 * of user inactivity, minimizing API traffic while ensuring data safety.
 */
const debouncedSave = debounce(() => {
    if (!isReadOnly.value) {
        handleSave()
    }
}, 2000)

/**
 * Reactive Watcher for Content Changes.
 * Automatically updates the R Markdown structure in the store whenever 
 * the editor title or content is modified.
 */
watch([cleanContent, notebookTitle], () => {
    if (!isReadOnly.value) {
        store.notebook.content = generateFullRmd()
        store.notebook.title = notebookTitle.value
        debouncedSave()
    }
})

/**
 * Toggles notebook visibility.
 * Public: Visible in global feed, searchable by author.
 * Private: Restricted to the owner.
 */
const handlePublicToggle = async () => {
    if (isReadOnly.value) return
    store.notebook.is_public = isPublic.value
    await handleSave()
}

/**
 * Persists current notebook state to the backend.
 * Handles URL updates if a 'new' notebook receives its first database ID.
 */
const handleSave = async () => {
    if (isReadOnly.value) return
    const savedId = await store.save()
    if (savedId && route.params.id === 'new') {
        router.push(`/notebook/${savedId}`)
        notebook.value.id = savedId
    }
}

/**
 * Access Control Logic.
 * Computes if the current user has permission to edit the notebook.
 * Read-only mode is active if the notebook is public and the author 
 * does not match the logged-in user.
 */
const isReadOnly = computed(() => {
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
    return notebook.value.is_public && notebook.value.author !== currentUser.username
})

/**
 * Reproducibility Validation (RDiff).
 * Triggers a Docker container execution to compare outputs from the 
 * isolated environment against the local run.
 */
const handleDiff = async () => {
    await store.runDiff()
    if (diffResult.value) {
        showDiffModal.value = true
    }
}

/**
 * Local Export.
 * Generates and downloads the raw .Rmd file directly from browser memory.
 */
const downloadRmd = () => {
    const fullContent = generateFullRmd()
    const blob = new Blob([fullContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${notebookTitle.value}.Rmd`
    a.click()
    URL.revokeObjectURL(url)
}

/**
 * UI Utility: Resizable Pane.
 * Manages the mouse events for adjusting the width of the editor vs output pane.
 */
const startResize = (e: MouseEvent) => {
    const startX = e.clientX
    const startWidth = paneWidth.value
    const onMove = (e: MouseEvent) => {
        const newWidth = startWidth + (e.clientX - startX)
        if (newWidth > 200 && newWidth < window.innerWidth - 300) {
            paneWidth.value = newWidth
        }
    }
    const onUp = () => {
        document.removeEventListener('mousemove', onMove)
        document.removeEventListener('mouseup', onUp)
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
}

/**
 * Performance Helper: Debounce function.
 * Ensures high-frequency events (like typing) do not overwhelm the backend.
 */
function debounce<T extends (...args: unknown[]) => unknown>(
    fn: T,
    delay: number
): (...args: Parameters<T>) => void {
    let timeout: number | undefined
    return (...args: Parameters<T>) => {
        clearTimeout(timeout)
        timeout = setTimeout(() => fn(...args), delay)
    }
}

const adjustedIssues = computed(() => {
    return staticAnalysis.value?.issues || []
})
</script>

<template>
    <div class="notebook-editor" :class="{ 'read-only-mode': isReadOnly }">
        <div v-if="isReadOnly" class="read-only-banner">
            <i class="fas fa-eye"></i>
            <span>Viewing public notebook by <strong>{{ notebook.author }}</strong></span>
            <span class="separator">•</span>
            <span>Read-only mode</span>
        </div>

        <div class="editor-header">
            <div class="title-section">
                <input v-model="notebookTitle" @blur="handleSave" class="notebook-title" placeholder="Untitled Notebook"
                    :disabled="isReadOnly" :class="{ 'read-only': isReadOnly }" data-testid="notebook-title-input">

                <label v-if="!isReadOnly" class="public-toggle" id="public-toggle">
                    <input type="checkbox" v-model="isPublic" @change="handlePublicToggle"
                        data-testid="public-toggle-checkbox">
                    <span class="toggle-label">
                        <i class="fas" :class="isPublic ? 'fa-globe' : 'fa-lock'"></i>
                        {{ isPublic ? 'Public' : 'Private' }}
                    </span>
                    <span class="info-icon" title="Public: Anyone can view with link | Private: Only you can access">
                        <i class="fas fa-info-circle"></i>
                    </span>
                </label>

                <span v-else class="public-badge ">
                    <i class="fas fa-globe"></i> Public
                </span>
            </div>

            <EditorToolbar :is-executing="executing" :is-generating="packageGenerating" :is-diffing="diffGenerating"
                :is-downloading="packageLoading" :has-executed="hasExecuted" :has-package="hasPackage"
                :can-diff="canGenerateDiff" :can-download="canDownloadPackage" :is-public="isPublic"
                :is-read-only="isReadOnly" :notebook-id="notebook.id" @save="handleSave" @run="store.runLocal"
                @generate="store.runPackage" @diff="handleDiff" @toggleAnalysis="showAnalysis = true"
                @downloadRmd="downloadRmd" @download="store.downloadPackage" />
        </div>

        <div class="editor-split-view">
            <div class="editor-pane" :style="{ width: paneWidth + 'px' }">
                <div class="pane-header">
                    <h3><i class="fas fa-code"></i> R Script</h3>

                    <div class="editor-status">
                        <span v-if="warnings.length > 0" class="warning-badge" @click="showAnalysis = true"
                            style="cursor: pointer;">
                            <i class="fas fa-exclamation-triangle"></i> {{ warnings.length }} warnings
                        </span>
                    </div>
                </div>

                <textarea ref="editorTextarea" v-model="cleanContent" @input="debouncedSave" class="rmarkdown-editor"
                    :placeholder="placeholderText" :class="{ 'has-warnings': warnings.length > 0 }"
                    :readonly="isReadOnly" :disabled="isReadOnly" data-testid="notebook-content-textarea"></textarea>
            </div>

            <div class="resize-handle" @mousedown="startResize"></div>

            <div class="output-pane">
                <OutputPane :result="executionResult" :error="executionError" :is-loading="executing" />
            </div>
        </div>

        <Transition name="slide-up">
            <AnalysisDrawer v-if="showAnalysis && (analysis || staticAnalysis)" :issues="adjustedIssues"
                :code="cleanContent" :diff-result="diffResult" :package-loading="packageLoading" :r4r-data="r4rData"
                :has-static-analysis="!!staticAnalysis" :is-read-only="isReadOnly" @close="showAnalysis = false"
                @openDiff="showDiffModal = true" @download="store.downloadPackage" />
        </Transition>

        <Transition name="fade">
            <div v-if="showDiffModal" class="modal-overlay" @click="showDiffModal = false">
                <DiffModal :diff-html="diffResult" @close="showDiffModal = false" />
            </div>
        </Transition>
    </div>
</template>