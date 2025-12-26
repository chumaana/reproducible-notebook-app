<template>
    <div class="notebook-editor">
        <div class="editor-header">
            <input v-model="notebookTitle" @blur="updateTitle" class="notebook-title" placeholder="Untitled Notebook">

            <div class="editor-actions">
                <button @click="saveNotebook" class="btn btn-primary">
                    <i class="fas fa-save"></i> Save
                </button>
                <button @click="executeNotebook" class="btn btn-success" :disabled="executing">
                    <i class="fas fa-play"></i> {{ executing ? 'Running...' : 'Run' }}
                </button>
                <button @click="toggleAnalysis" class="btn btn-secondary" :disabled="!notebook.id">
                    <i class="fas fa-chart-bar"></i> Analysis
                </button>
                <button @click="downloadRmd" class="btn btn-outline">
                    <i class="fas fa-download"></i> .Rmd
                </button>

                <button @click="downloadPackage" class="btn btn-outline" :disabled="!isPackageReady || packageLoading"
                    :title="!isPackageReady ? 'Run the notebook first to generate package' : 'Download ZIP'">
                    <i class="fas" :class="packageLoading ? 'fa-spinner fa-spin' : 'fa-box'"></i>
                    {{ packageLoading ? 'Preparing...' : 'Package' }}
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
                        <span v-if="executing" class="status-running">
                            <i class="fas fa-spinner fa-spin"></i> Running...
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

                    <div v-if="adjustedIssues.length > 0" class="error-actions">
                        <p>The analyzer detected potential issues with your code:</p>
                        <button @click="showAnalysis = true" class="btn btn-sm btn-outline">
                            <i class="fas fa-search"></i> View Analysis Report ({{ adjustedIssues.length }} issues)
                        </button>
                    </div>
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
                                <span class="issue-count">
                                    Line(s): {{issue.lines.map((l: any) => l.line_number).join(', ')}}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div v-if="adjustedIssues.length > 0" class="section">
                        <h4><i class="fas fa-code"></i> Your Code</h4>
                        <CodeHighlighter :code="cleanContent" :issues="adjustedIssues" />
                    </div>

                    <div v-if="adjustedIssues.length === 0 && staticAnalysis" class="section">
                        <div class="success-banner">
                            <i class="fas fa-check-circle"></i>
                            <span>No reproducibility issues detected!</span>
                        </div>
                    </div>

                    <div v-if="analysis && (analysis.detected_packages || []).length > 0" class="section">
                        <h4><i class="fas fa-cube"></i> R Packages ({{ analysis.detected_packages.length }})</h4>
                        <div class="package-tags">
                            <span v-for="pkg in (analysis.detected_packages || [])" :key="pkg" class="package-tag">
                                {{ pkg }}
                            </span>
                        </div>
                    </div>

                    <div v-if="analysis && analysis.manifest && analysis.manifest.system_packages" class="section">
                        <h4><i class="fas fa-server"></i> System Dependencies</h4>
                        <div class="sys-deps">
                            <span v-for="dep in analysis.manifest.system_packages.slice(0, 8)" :key="dep"
                                class="sys-dep-tag">
                                {{ dep }}
                            </span>
                            <span v-if="analysis.manifest.system_packages.length > 8" class="more-deps">
                                +{{ analysis.manifest.system_packages.length - 8 }} more
                            </span>
                        </div>
                    </div>

                    <div class="modal-actions">
                        <button @click="downloadPackageFromModal" class="btn btn-sm btn-primary"
                            :disabled="!isPackageReady || packageLoading">
                            <i class="fas" :class="packageLoading ? 'fa-spinner fa-spin' : 'fa-download'"></i>
                            {{ packageLoading ? 'Preparing...' : 'Download Reproducibility Package' }}
                        </button>
                    </div>
                </div>
            </div>
        </Transition>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import CodeHighlighter from '@/components/CodeHighlighter.vue'

const route = useRoute()

const notebook = ref<any>({
    title: 'Untitled Notebook',
    content: ''
})

const notebookTitle = ref('Untitled Notebook')
const cleanContent = ref('')
const warnings = ref<any[]>([])

const executing = ref(false)
const executionResult = ref<string | null>(null)
const executionError = ref<string | null>(null)
const errorPre = ref<HTMLElement | null>(null)

const analysis = ref<any>(null)
const staticAnalysis = ref<any>(null)
const showAnalysis = ref(false)
const editorTextarea = ref<HTMLTextAreaElement | null>(null)
const packageLoading = ref(false)

let resizeStartX = 0
let resizeStartWidth = 0
let isResizing = false

const parsedError = computed(() => {
    if (!executionError.value) return null;
    const errorMatch = executionError.value.match(/(Error in[\s\S]+?Execution halted)|(Error:[\s\S]+)|(! cannot open[\s\S]+)/);
    if (errorMatch) {
        return errorMatch[0].trim();
    }
    const lines = executionError.value.split('\n');
    return lines.slice(-10).join('\n');
});

const isPackageReady = computed(() => {
    if (!analysis.value) return false
    return !!(analysis.value.manifest || analysis.value.dockerfile)
})

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

const adjustedIssues = computed(() => {
    if (!staticAnalysis.value || !staticAnalysis.value.issues) return []

    return staticAnalysis.value.issues.map((issue: any) => ({
        ...issue,
        lines: issue.lines.map((line: any) => ({
            ...line,
            line_number: Math.max(1, line.line_number - totalOffset.value)
        })).filter((l: any) => l.line_number > 0)
    }))
})

const placeholderText = `# Write your R code here
library(ggplot2)

data <- mtcars
summary(data)

ggplot(data, aes(x=wt, y=mpg)) + 
  geom_point() +
  geom_smooth(method='lm')
`

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

watch(
    () => notebook.value.content,
    (newContent) => {
        if (newContent) {
            cleanContent.value = extractCleanContent(newContent)
        }
    }
)

watch(notebookTitle, () => {
    notebook.value.title = notebookTitle.value
})

const loadNotebook = async () => {
    const id = route.params.id as string
    if (id && id !== 'new') {
        try {
            const data = await api.getNotebook(id)
            notebook.value = data
            notebookTitle.value = data.title
            cleanContent.value = extractCleanContent(data.content)
            await loadAnalysis()
        } catch (error) {
            console.error('Failed to load notebook:', error)
        }
    }
}

const updateTitle = async () => {
    notebook.value.title = notebookTitle.value
    await saveNotebook()
}

const saveNotebook = async () => {
    notebook.value.content = generateFullRmd()

    try {
        if (notebook.value.id) {
            await api.updateNotebook(notebook.value.id, notebook.value)
        } else {
            const created = await api.createNotebook(notebook.value)
            notebook.value = created
            notebookTitle.value = created.title
        }
    } catch (error) {
        console.error('Save failed:', error)
    }
}

const debouncedSave = debounce(() => {
    saveNotebook()
}, 2000)

const executeNotebook = async () => {
    if (!notebook.value.id) {
        await saveNotebook()
    }

    executing.value = true
    executionResult.value = null
    executionError.value = null
    warnings.value = []

    try {
        const result = await api.executeNotebook(notebook.value.id)

        if (result.static_analysis) {
            staticAnalysis.value = result.static_analysis
            warnings.value = result.static_analysis.issues || []
        }

        if (result.success === false) {
            executionError.value = result.error || 'Execution failed'
            return
        }

        executionResult.value = result.html

        analysis.value = {
            ...analysis.value,
            manifest: result.manifest,
            detected_packages: result.detected_packages,
            dockerfile: result.dockerfile,
        }

        await loadAnalysis()

    } catch (error: any) {
        console.error('Execution failed:', error)

        if (error.response && error.response.data) {
            executionError.value = error.response.data.error || JSON.stringify(error.response.data)

            if (error.response.data.static_analysis) {
                staticAnalysis.value = error.response.data.static_analysis
                warnings.value = error.response.data.static_analysis.issues || []
            }
        } else {
            executionError.value = `Network Error: ${error.message}`
        }
    } finally {
        executing.value = false
    }


}


const loadAnalysis = async () => {
    if (!notebook.value.id) return
    try {
        const data = await api.getReproducibilityAnalysis(notebook.value.id)
        analysis.value = data

        if (data.static_analysis) {
            staticAnalysis.value = data.static_analysis
            warnings.value = data.static_analysis.issues || []
        }

    } catch (error) {
        console.error('Failed to load analysis:', error)
    }
}

const toggleAnalysis = async () => {
    if (!analysis.value && !staticAnalysis.value) {
        await loadAnalysis()
    }
    showAnalysis.value = !showAnalysis.value
}

const downloadRmd = () => {
    const fullContent = generateFullRmd()
    downloadFile(fullContent, `${notebookTitle.value}.Rmd`, 'text/plain')
}
const downloadPackage = async () => {
    if (!notebook.value.id || packageLoading.value || !isPackageReady.value) return

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

    } catch (error) {
        console.error('Download failed:', error)
        alert('Failed to download package.')
    } finally {
        setTimeout(() => {
            packageLoading.value = false
        }, 1000)
    }
}

const downloadPackageFromModal = downloadPackage

const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
}

const startResize = (e: MouseEvent) => {
    isResizing = true
    resizeStartX = e.clientX
    const editorPane = document.querySelector('.editor-pane') as HTMLElement
    resizeStartWidth = editorPane.offsetWidth
    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', stopResize)
}

const onMouseMove = (e: MouseEvent) => {
    if (!isResizing) return
    const editorPane = document.querySelector('.editor-pane') as HTMLElement
    const newWidth = resizeStartWidth + (e.clientX - resizeStartX)
    if (newWidth > 200 && newWidth < window.innerWidth - 200) {
        editorPane.style.flex = `0 0 ${newWidth}px`
    }
}

const stopResize = () => {
    isResizing = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', stopResize)
}

function debounce<T extends (...args: any[]) => any>(fn: T, delay: number) {
    let timeout: any
    return (...args: Parameters<T>) => {
        clearTimeout(timeout)
        timeout = setTimeout(() => fn(...args), delay)
    }
}

onMounted(() => {
    loadNotebook()
})
</script>

<style scoped>
.notebook-editor {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #f5f5f5;
}

.editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: white;
    border-bottom: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    z-index: 10;
}

.notebook-title {
    font-size: 1.25rem;
    font-weight: 600;
    border: none;
    outline: none;
    padding: 0.5rem;
    border-radius: 4px;
    min-width: 300px;
}

.notebook-title:focus {
    background: #f9fafb;
}

.editor-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.editor-split-view {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.editor-pane,
.output-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
    overflow: hidden;
}

.pane-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.5rem;
    background: #fafafa;
    border-bottom: 1px solid #e5e7eb;
}

.pane-header h3 {
    margin: 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: #6b7280;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.editor-status {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.warning-badge {
    background: #fef3c7;
    color: #d97706;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.output-status {
    font-size: 0.875rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.status-running {
    color: #3b82f6;
}

.status-success {
    color: #10b981;
}

.status-error {
    color: #dc2626;
    font-weight: 600;
}

.status-empty {
    color: #6b7280;
}

.rmarkdown-editor {
    flex: 1;
    padding: 2rem;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 14px;
    line-height: 1.8;
    border: none;
    resize: none;
    outline: none;
    background: white;
    color: #1f2937;
    overflow-y: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.rmarkdown-editor::placeholder {
    color: #9ca3af;
}

.resize-handle {
    width: 4px;
    background: #e5e7eb;
    cursor: col-resize;
    transition: background 0.2s;
}

.resize-handle:hover {
    background: #6366f1;
}

.output-content {
    flex: 1;
    overflow: hidden;
}

.output-iframe {
    width: 100%;
    height: 100%;
    border: none;
    background: white;
}

.output-error {
    padding: 2rem;
    background: #fff5f5;
    height: 100%;
    overflow-y: auto;
}

.error-banner {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #b91c1c;
    font-size: 1.25rem;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #fecaca;
}

/* 🔥 Highlighted Error Box */
.highlighted-error {
    background: #fee2e2;
    border-left: 5px solid #dc2626;
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 4px;
}

.highlighted-error h4 {
    margin: 0 0 0.5rem 0;
    color: #991b1b;
    font-size: 0.9rem;
    font-weight: 700;
}

.highlighted-error pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: 'JetBrains Mono', monospace;
    color: #7f1d1d;
    font-size: 0.9rem;
    font-weight: 600;
}

/* Details/Summary styles */
.full-log-details summary {
    cursor: pointer;
    color: #6b7280;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
    user-select: none;
}

.full-log-details summary:hover {
    color: #374151;
}

.error-details {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    background: #1e1e1e;
    color: #9ca3af;
    padding: 1rem;
    border-radius: 8px;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 200px;
    overflow-y: auto;
}

.error-actions {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #fecaca;
    color: #7f1d1d;
}

.output-empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #9ca3af;
    padding: 2rem;
}

.output-empty i {
    font-size: 4rem;
    margin-bottom: 1rem;
    color: #d1d5db;
}

.output-empty p {
    font-size: 1rem;
}

/* Analysis Modal */
.analysis-modal-bottom {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 480px;
    max-height: 80vh;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.modal-header-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: #6366f1;
    color: white;
}

.modal-header-bottom h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.modal-close-btn {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.modal-close-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: rotate(90deg);
}

.modal-body-bottom {
    padding: 1.5rem;
    overflow-y: auto;
    max-height: calc(80vh - 60px);
}

.section {
    margin-top: 1.25rem;
    padding-top: 1rem;
    border-top: 1px solid #f3f4f6;
}

.section:first-child {
    margin-top: 0;
    padding-top: 0;
    border-top: none;
}

.section h4 {
    font-size: 0.875rem;
    color: #374151;
    margin: 0 0 0.75rem 0;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.issues-summary {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.issue-summary-card {
    padding: 12px;
    border-radius: 8px;
    border-left: 4px solid;
}

.issue-summary-card.severity-high {
    background: #fee2e2;
    border-left-color: #dc2626;
}

.issue-summary-card.severity-medium {
    background: #fef3c7;
    border-left-color: #f59e0b;
}

.issue-summary-card.severity-low {
    background: #dbeafe;
    border-left-color: #3b82f6;
}

.issue-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}

.severity-badge {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.1);
}

.issue-details {
    font-size: 13px;
    color: #6b7280;
    margin: 4px 0;
}

.issue-fix {
    font-size: 12px;
    color: #3b82f6;
    margin: 4px 0;
}

.issue-count {
    font-size: 11px;
    color: #9ca3af;
    font-weight: 600;
}

.success-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: #d1fae5;
    border-radius: 8px;
    color: #059669;
    font-weight: 600;
}

.success-banner i {
    font-size: 24px;
}

.package-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.package-tag {
    background: #f3f4f6;
    color: #6366f1;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid #e5e7eb;
}

.sys-deps {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.sys-dep-tag {
    background: #ede9fe;
    color: #7c3aed;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-family: monospace;
    font-weight: 600;
}

.more-deps {
    color: #9ca3af;
    font-size: 11px;
    font-weight: 600;
    align-self: center;
}

.modal-actions {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid #f3f4f6;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.btn {
    padding: 0.5rem 1rem;
    border-radius: 6px;
    border: none;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-primary {
    background: #6366f1;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: #4f46e5;
}

.btn-success {
    background: #10b981;
    color: white;
}

.btn-success:hover:not(:disabled) {
    background: #059669;
}

.btn-secondary {
    background: #8b5cf6;
    color: white;
}

.btn-secondary:hover:not(:disabled) {
    background: #7c3aed;
}

.btn-outline {
    background: white;
    border: 1px solid #d1d5db;
    color: #374151;
}

.btn-outline:hover:not(:disabled) {
    background: #f9fafb;
}

.btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    width: 100%;
    justify-content: center;
}

.slide-up-enter-active,
.slide-up-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from {
    opacity: 0;
    transform: translateY(20px);
}

.slide-up-leave-to {
    opacity: 0;
    transform: translateY(20px);
}
</style>