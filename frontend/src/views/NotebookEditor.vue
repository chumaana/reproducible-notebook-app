<template>
    <div class="notebook-editor">
        <div class="editor-header">
            <input v-model="notebookTitle" @blur="updateTitle" class="notebook-title" placeholder="Untitled Notebook">

            <div class="editor-actions">
                <button @click="saveNotebook" class="btn btn-primary">
                    <i class="fas fa-save"></i> Save
                </button>

                <button @click="executeNotebook" class="btn btn-success" :disabled="executing">
                    <i class="fas" :class="executing ? 'fa-spinner fa-spin' : 'fa-play'"></i>
                    {{ executing ? 'Running...' : 'Run' }}
                </button>

                <button v-if="!canDownloadPackage" @click="generatePackage" class="btn btn-primary"
                    :disabled="packageGenerating || !hasExecuted"
                    :title="!hasExecuted ? 'Run notebook first' : 'Content changed! Generate new package.'">
                    <i class="fas" :class="packageGenerating ? 'fa-spinner fa-spin' : 'fa-box'"></i>
                    {{ packageGenerating ? 'Building...' : 'Generate Package' }}
                </button>

                <button v-if="hasPackage && canDownloadPackage" @click="generatePackage" class="btn btn-primary"
                    title="Force Re-build Package">
                    <i class="fas fa-sync-alt" :class="{ 'fa-spin': packageGenerating }"></i>
                </button>

                <button @click="generateDiff" class="btn btn-secondary" :disabled="diffGenerating || !canGenerateDiff"
                    :title="!canGenerateDiff ? 'Wait for Local Run and Package Generation' : 'Compare local vs container'">
                    <i class="fas" :class="diffGenerating ? 'fa-spinner fa-spin' : 'fa-code-compare'"></i>
                    {{ diffGenerating ? 'Comparing...' : 'Diff' }}
                </button>

                <button @click="toggleAnalysis" class="btn btn-outline" :disabled="!notebook.id">
                    <i class="fas fa-chart-bar"></i> Analysis
                </button>

                <button @click="downloadRmd" class="btn btn-outline">
                    <i class="fas fa-download"></i> .Rmd
                </button>

                <button v-if="canDownloadPackage" @click="downloadPackage" class="btn btn-outline"
                    :disabled="packageLoading">
                    <i class="fas" :class="packageLoading ? 'fa-spinner fa-spin' : 'fa-download'"></i>
                    {{ packageLoading ? 'Downloading...' : 'Download ZIP' }}
                </button>
            </div>
        </div>

        <div class="editor-split-view">
            <div class="editor-pane">
                <div class="pane-header">
                    <h3><i class="fas fa-code"></i> R Script</h3>
                    <div class="editor-status">
                        <span v-if="adjustedIssues.length > 0" class="warning-badge" @click="showAnalysis = true"
                            style="cursor: pointer;">
                            <i class="fas fa-exclamation-triangle"></i> {{ adjustedIssues.length }} warnings
                        </span>

                    </div>
                </div>

                <textarea ref="editorTextarea" v-model="cleanContent" @input="debouncedSave" class="rmarkdown-editor"
                    :placeholder="placeholderText" :class="{ 'has-warnings': adjustedIssues.length > 0 }">
                </textarea>
            </div>

            <div class="resize-handle" @mousedown="startResize"></div>

            <div class="output-pane">
                <div class="pane-header">
                    <h3><i class="fas fa-file-alt"></i> Output</h3>
                    <div class="output-status">
                        <span v-if="executing || packageGenerating || diffGenerating" class="status-running">
                            <i class="fas fa-spinner fa-spin"></i>
                            {{ executing ? 'Running...' : packageGenerating ? 'Building...' : 'Comparing...' }}
                        </span>
                        <span v-else-if="executionError" class="status-error">
                            <i class="fas fa-times-circle"></i> Failed
                        </span>
                        <span v-else-if="executionResult" class="status-success">
                            <i class="fas fa-check-circle"></i> Ready
                        </span>
                        <span v-else class="status-empty">
                            <i class="fas fa-info-circle"></i> Run to see output
                        </span>
                    </div>
                </div>

                <div v-if="executionError" class="output-error">
                    <div class="error-banner">
                        <i class="fas fa-bomb"></i>
                        <strong>Execution Failed</strong>
                    </div>

                    <div class="highlighted-error">
                        <h4><i class="fas fa-bug"></i> Critical Error:</h4>
                        <pre>{{ parsedError }}</pre>
                    </div>

                    <details class="full-log-details">
                        <summary>Show Full System Log (Debug)</summary>
                        <pre ref="errorPre" class="error-details">{{ executionError }}</pre>
                    </details>
                </div>

                <div v-else-if="executionResult" class="output-content">
                    <iframe :srcdoc="executionResult" class="output-iframe"></iframe>
                </div>

                <div v-else class="output-empty">
                    <i class="fas fa-play-circle"></i>
                    <p>Click "Run" to execute your notebook</p>
                </div>
            </div>
        </div>

        <Transition name="slide-up">
            <div v-if="showAnalysis && (analysis || staticAnalysis)" class="analysis-modal-bottom">
                <div class="modal-header-bottom">
                    <h3><i class="fas fa-chart-bar"></i> Reproducibility Analysis</h3>
                    <button @click="showAnalysis = false" class="modal-close-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="modal-body-bottom">
                    <div v-if="adjustedIssues.length > 0" class="section">
                        <h4><i class="fas fa-exclamation-triangle"></i> Non-Reproducibility Issues</h4>
                        <div class="issues-summary">
                            <div v-for="issue in adjustedIssues" :key="issue.category" class="issue-summary-card"
                                :class="`severity-${issue.severity}`">
                                <div class="issue-header">
                                    <span class="severity-badge">{{ issue.severity }}</span>
                                    <strong>{{ issue.title }}</strong>
                                </div>
                                <p class="issue-details">{{ issue.details }}</p>
                                <p class="issue-fix">💡 {{ issue.fix }}</p>
                                <span class="issue-count">Line(s): {{issue.lines.map((l: any) =>
                                    l.line_number).join(',')}}</span>
                            </div>
                        </div>
                    </div>

                    <div v-if="adjustedIssues.length > 0" class="section">
                        <h4><i class="fas fa-code"></i> Code Context</h4>
                        <CodeHighlighter :code="cleanContent" :issues="adjustedIssues" />
                    </div>

                    <div v-if="adjustedIssues.length === 0 && staticAnalysis" class="section">
                        <div class="success-banner">
                            <i class="fas fa-check-circle"></i> <span>No reproducibility issues detected!</span>
                        </div>
                    </div>

                    <div class="modal-actions">
                        <button v-if="diffResult" @click="showDiffModal = true" class="btn btn-sm btn-secondary">
                            <i class="fas fa-code-compare"></i>
                            View Semantic Diff
                        </button>

                        <button @click="downloadPackageFromModal" class="btn btn-sm btn-primary"
                            :disabled="packageLoading">
                            <i class="fas" :class="packageLoading ? 'fa-spinner fa-spin' : 'fa-download'"></i>
                            {{ packageLoading ? 'Downloading...' : 'Download Reproducibility Package' }}
                        </button>
                    </div>


                </div>
            </div>
        </Transition>

        <Transition name="fade">
            <div v-if="showDiffModal" class="modal-overlay" @click="showDiffModal = false">
                <div class="diff-modal" @click.stop>
                    <div class="diff-modal-header">
                        <h3><i class="fas fa-code-compare"></i> Semantic Diff</h3>
                        <button @click="showDiffModal = false" class="modal-close-btn"><i
                                class="fas fa-times"></i></button>
                    </div>
                    <div class="diff-modal-body">
                        <iframe v-if="diffResult" :srcdoc="diffResult" class="diff-iframe"></iframe>
                        <div v-else class="diff-empty"><i class="fas fa-spinner fa-spin"></i>
                            <p>Loading diff...</p>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>
    </div>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useNotebookStore } from '@/stores/notebookStore' // Adjust path if needed
import CodeHighlighter from '@/components/CodeHighlighter.vue'

// --- 1. Setup Store & Route ---
const route = useRoute()
const store = useNotebookStore()

// We use storeToRefs to keep reactivity for state properties
const {
    notebook,
    analysis,
    staticAnalysis,
    warnings,            // Combined list of issues from store
    executing,
    packageGenerating,
    diffGenerating,
    packageLoading,
    executionResult,
    executionError,
    diffResult,
    hasExecuted,
    hasPackage,
    canGenerateDiff,
    canDownloadPackage,  // Logic handled in store
    isPackageUpToDate    // Logic handled in store
} = storeToRefs(store)

// --- 2. Local UI State ---
const notebookTitle = ref('Untitled Notebook')
const cleanContent = ref('')
const showAnalysis = ref(false)
const showDiffModal = ref(false)
const editorTextarea = ref<HTMLTextAreaElement | null>(null)

// Resizing logic vars
let resizeStartX = 0
let resizeStartWidth = 0
let isResizing = false

// --- 3. Computed UI Helpers ---

// Format the error message for the UI
const parsedError = computed(() => {
    if (!executionError.value) return null
    const errorMatch = executionError.value.match(/(Error in[\s\S]+?Execution halted)|(Error:[\s\S]+)|(! cannot open[\s\S]+)/)
    if (errorMatch) {
        return errorMatch[0].trim()
    }
    const lines = executionError.value.split('\n')
    return lines.slice(-10).join('\n')
})

// Calculate line offsets for mapping errors to the editor
const shouldAutoWrap = computed(() => {
    return !cleanContent.value.includes('```{r}')
})

const totalOffset = computed(() => {
    const yaml = `---
title: "${notebookTitle.value}"
output: html_document
---

`
    const wrapperOffset = shouldAutoWrap.value ? 1 : 0
    return (yaml.split('\n').length - 1) + wrapperOffset
})

// Map store warnings to specific lines in the local editor
const adjustedIssues = computed(() => {
    const rawIssues = warnings.value || []
    if (rawIssues.length === 0) return []

    return rawIssues.map((issue: any) => {
        let linesData = []

        if (issue.lines && Array.isArray(issue.lines)) {
            linesData = issue.lines.map((l: any) => ({
                line_number: Math.max(1, l.line_number - totalOffset.value),
                code: l.content || ''
            })).filter((l: any) => l.line_number > 0)
        } else {
            // Default to line 1 if no specific line provided
            linesData = [{ line_number: 1, code: 'Global Issue' }]
        }

        return {
            ...issue,
            lines: linesData
        }
    })
})

const placeholderText = `# Write your R code here
library(ggplot2)

data <- mtcars
summary(data)

ggplot(data, aes(x=wt, y=mpg)) + 
  geom_point() +
  geom_smooth(method='lm')
`

// --- 4. Content Processing ---

const extractCleanContent = (content: string): string => {
    if (!content) return ''
    const yamlRegex = /^---\s*\n[\s\S]*?\n---\s*\n/

    let clean = content.replace(yamlRegex, '').trim()

    if (clean.startsWith('```{r}') && clean.endsWith('```')) {
        clean = clean.replace(/^```\{r\}\n/, '').replace(/\n```$/, '')
    }

    return clean
}

const generateFullRmd = (): string => {
    const header = `---
title: "${notebookTitle.value}"
output: html_document
---

`
    if (shouldAutoWrap.value) {
        return header + '```{r}\n' + cleanContent.value + '\n```'
    }

    return header + cleanContent.value
}

// --- 5. Watchers & Lifecycle ---

// Watch for store data load to update local inputs
watch(() => notebook.value, (newVal) => {
    if (newVal) {
        if (newVal.title) notebookTitle.value = newVal.title
        // Only update content if it differs significantly to prevent cursor jumping
        const extracted = extractCleanContent(newVal.content)
        if (extracted !== cleanContent.value) {
            cleanContent.value = extracted
        }
    }
}, { deep: true })

// Watch local content to update store state
watch(cleanContent, (newVal) => {
    notebook.value.content = generateFullRmd()
})

// Watch local title to update store state
watch(notebookTitle, () => {
    notebook.value.title = notebookTitle.value
})

onMounted(async () => {
    const id = route.params.id as string

    if (id && id !== 'new') {
        // Case A: Editing an existing notebook
        await store.load(id)
    } else {
        // Case B: Creating a new notebook
        // We MUST reset the store to clear previous results/analysis
        store.resetState()

        // Reset local UI state
        notebookTitle.value = 'Untitled Notebook'
        cleanContent.value = ''
    }

    // Sync local refs with whatever is now in the store
    // (This handles both cases: ensuring title is correct for existing, 
    // or empty for new)
    notebookTitle.value = notebook.value.title
    cleanContent.value = extractCleanContent(notebook.value.content)
})

// --- 6. Actions (Mapped to Store) ---

const updateTitle = async () => {
    await store.save()
}

// Debounce save to prevent API flooding
const debouncedSave = debounce(() => {
    store.save()
}, 2000)

const saveNotebook = () => store.save()

const executeNotebook = () => store.runLocal()

// Logic for generating package handled by store
const generatePackage = () => store.runPackage()

// Logic for downloading package handled by store
const downloadPackage = () => store.downloadPackage()

// Wrapper for modal download button
const downloadPackageFromModal = () => store.downloadPackage()

const generateDiff = async () => {
    await store.runDiff()
    if (diffResult.value) {
        showDiffModal.value = true
    }
}

const toggleAnalysis = () => {
    showAnalysis.value = !showAnalysis.value
}

// Purely client-side .Rmd download
const downloadRmd = () => {
    const fullContent = generateFullRmd()
    downloadFile(fullContent, `${notebookTitle.value}.Rmd`, 'text/plain')
}

// Helper to download string content
const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
}

// --- 7. Resizing Logic ---

const startResize = (e: MouseEvent) => {
    isResizing = true
    resizeStartX = e.clientX
    const editorPane = document.querySelector('.editor-pane') as HTMLElement
    if (editorPane) {
        resizeStartWidth = editorPane.offsetWidth
        document.addEventListener('mousemove', onMouseMove)
        document.addEventListener('mouseup', stopResize)
    }
}

const onMouseMove = (e: MouseEvent) => {
    if (!isResizing) return
    const editorPane = document.querySelector('.editor-pane') as HTMLElement
    if (editorPane) {
        const newWidth = resizeStartWidth + (e.clientX - resizeStartX)
        if (newWidth > 200 && newWidth < window.innerWidth - 200) {
            editorPane.style.flex = `0 0 ${newWidth}px`
        }
    }
}

const stopResize = () => {
    isResizing = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', stopResize)
}

// Utility
function debounce<T extends (...args: any[]) => any>(fn: T, delay: number) {
    let timeout: any
    return (...args: Parameters<T>) => {
        clearTimeout(timeout)
        timeout = setTimeout(() => fn(...args), delay)
    }
}
</script>