<template>
    <div class="notebook-editor">
        <!-- Header -->
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
                    <i class="fas fa-download"></i> Download .Rmd
                </button>
                <button @click="downloadPackage" class="btn btn-outline" :disabled="!notebook.id || packageLoading">
                    <i class="fas" :class="packageLoading ? 'fa-spinner fa-spin' : 'fa-box'"></i>
                    {{ packageLoading ? 'Preparing...' : 'Download Package' }}
                </button>
            </div>
        </div>

        <!-- Split View: Editor | Output -->
        <div class="editor-split-view">
            <!-- Left: Editor -->
            <div class="editor-pane">
                <div class="pane-header">
                    <h3><i class="fas fa-code"></i> Editor</h3>
                    <div class="editor-status">
                        <span v-if="warnings.length > 0" class="warning-badge">
                            <i class="fas fa-exclamation-triangle"></i> {{ warnings.length }} warnings
                        </span>
                    </div>
                </div>
                <textarea ref="editorTextarea" v-model="cleanContent" @input="debouncedSave" class="rmarkdown-editor"
                    :placeholder="placeholderText" :class="{ 'has-warnings': warnings.length > 0 }"></textarea>
            </div>

            <!-- Resize Handle -->
            <div class="resize-handle" @mousedown="startResize"></div>

            <!-- Right: Output -->
            <div class="output-pane">
                <div class="pane-header">
                    <h3><i class="fas fa-file-alt"></i> Output</h3>
                    <div class="output-status">
                        <span v-if="executing" class="status-running">
                            <i class="fas fa-spinner fa-spin"></i> Running...
                        </span>
                        <span v-else-if="executionResult" class="status-success">
                            <i class="fas fa-check-circle"></i> Ready
                        </span>
                        <span v-else class="status-empty">
                            <i class="fas fa-info-circle"></i> Run to see output
                        </span>
                    </div>
                </div>

                <div v-if="executionResult" class="output-content">
                    <iframe :srcdoc="executionResult" class="output-iframe"></iframe>
                </div>

                <div v-else class="output-empty">
                    <i class="fas fa-play-circle"></i>
                    <p>Click "Run" to execute your notebook</p>
                </div>
            </div>
        </div>

        <!-- Analysis Modal - Bottom Right -->
        <Transition name="slide-up">
            <div v-if="showAnalysis && analysis" class="analysis-modal-bottom">
                <div class="modal-header-bottom">
                    <h3><i class="fas fa-chart-bar"></i> Reproducibility Analysis</h3>
                    <button @click="showAnalysis = false" class="modal-close-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="modal-body-bottom">

                    <!-- 🔥 Static Analysis Issues -->
                    <div v-if="staticAnalysis && staticAnalysis.issues.length > 0" class="section">
                        <h4><i class="fas fa-exclamation-triangle"></i> Non-Reproducibility Issues</h4>
                        <div class="issues-summary">
                            <div v-for="issue in staticAnalysis.issues" :key="issue.category" class="issue-summary-card"
                                :class="`severity-${issue.severity}`">
                                <div class="issue-header">
                                    <span class="severity-badge">{{ issue.severity }}</span>
                                    <strong>{{ issue.title }}</strong>
                                </div>
                                <p class="issue-details">{{ issue.details }}</p>
                                <p class="issue-fix">💡 {{ issue.fix }}</p>
                                <span class="issue-count">{{ issue.lines.length }} location(s)</span>
                            </div>
                        </div>
                    </div>

                    <!-- 🔥 Code Viewer з Highlighting -->
                    <div v-if="staticAnalysis && staticAnalysis.issues.length > 0" class="section">
                        <h4><i class="fas fa-code"></i> Your Code</h4>
                        <CodeHighlighter :code="cleanContent" :issues="staticAnalysis.issues" />
                    </div>

                    <!-- ✅ No Issues Badge -->
                    <div v-if="staticAnalysis && staticAnalysis.issues.length === 0" class="section">
                        <div class="success-banner">
                            <i class="fas fa-check-circle"></i>
                            <span>No reproducibility issues detected!</span>
                        </div>
                    </div>

                    <!-- r4r Dependencies -->
                    <div v-if="(analysis.detected_packages || []).length > 0" class="section">
                        <h4><i class="fas fa-cube"></i> R Packages ({{ analysis.detected_packages.length }})</h4>
                        <div class="package-tags">
                            <span v-for="pkg in (analysis.detected_packages || [])" :key="pkg" class="package-tag">
                                {{ pkg }}
                            </span>
                        </div>
                    </div>

                    <!-- r4r System Dependencies -->
                    <div v-if="analysis.manifest && analysis.manifest.system_packages" class="section">
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

                    <!-- Dockerfile Preview -->
                    <div v-if="analysis.dockerfile" class="section">
                        <h4><i class="fab fa-docker"></i> Dockerfile</h4>
                        <pre class="dockerfile-preview">{{ analysis.dockerfile.substring(0, 300) }}...</pre>
                    </div>

                    <!-- Actions -->
                    <div class="modal-actions">
                        <button @click="downloadPackageFromModal" class="btn btn-sm btn-primary"
                            :disabled="packageLoading">
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
import { ref, onMounted, watch, nextTick } from 'vue'
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
const analysis = ref<any>(null)
const staticAnalysis = ref<any>(null)
const showAnalysis = ref(false)
const editorTextarea = ref<HTMLTextAreaElement | null>(null)
const packageLoading = ref(false)

let resizeStartX = 0
let resizeStartWidth = 0
let isResizing = false

const placeholderText = `## Introduction

Write your analysis here using Markdown and R code blocks.

\`\`\`{r}
# Load libraries
library(ggplot2)

# Your analysis
data <- mtcars
summary(data)

# Visualization
ggplot(data, aes(x=wt, y=mpg)) + 
  geom_point() +
  geom_smooth(method='lm')
\`\`\`

## Results

Add your findings and conclusions here.`

const extractCleanContent = (content: string): string => {
    if (!content) return ''
    const yamlRegex = /^---\s*\n[\s\S]*?\n---\s*\n/
    return content.replace(yamlRegex, '').trim()
}

const generateFullRmd = (): string => {
    const yaml = `---
title: "${notebookTitle.value}"
output: html_document
---

`
    return yaml + cleanContent.value
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

    try {
        const response = await fetch(
            `http://localhost:8000/api/notebooks/${notebook.value.id}/execute/`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            }
        )

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.error || `HTTP error! status: ${response.status}`)
        }

        const result = await response.json()
        console.log('Execute result:', result)
        executionResult.value = result.html

        // 🔥 Store analysis data from execution
        if (result.static_analysis) {
            staticAnalysis.value = result.static_analysis
            warnings.value = result.static_analysis.issues || []
        }

        // Auto-load full analysis
        if (notebook.value.id) {
            await loadAnalysis()
        }

    } catch (error: any) {
        console.error('Execution failed:', error)
        alert(`Execution failed: ${error.message}`)
    } finally {
        executing.value = false
    }
}

const loadAnalysis = async () => {
    if (!notebook.value.id) return

    try {
        const response = await fetch(
            `http://localhost:8000/api/notebooks/${notebook.value.id}/reproducibility/`
        )

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        analysis.value = data

        // 🔥 Load static analysis
        if (data.static_analysis) {
            staticAnalysis.value = data.static_analysis
            warnings.value = data.static_analysis.issues || []
        }

    } catch (error) {
        console.error('Failed to load analysis:', error)
    }
}

const toggleAnalysis = async () => {
    if (!analysis.value || !notebook.value.id) {
        await loadAnalysis()
    }
    showAnalysis.value = !showAnalysis.value
}

const downloadRmd = () => {
    const fullContent = generateFullRmd()
    downloadFile(fullContent, `${notebookTitle.value}.Rmd`, 'text/plain')
}

const downloadPackage = async () => {
    if (!notebook.value.id || packageLoading.value) return

    packageLoading.value = true

    try {
        const checkResponse = await fetch(
            `http://localhost:8000/api/notebooks/${notebook.value.id}/reproducibility/`
        )

        if (!checkResponse.ok) {
            alert('Please run the notebook first to generate the reproducibility package!')
            return
        }

        const url = `http://localhost:8000/api/notebooks/${notebook.value.id}/download_package/`
        window.open(url, '_blank')
    } catch (error) {
        console.error('Download failed:', error)
        alert('Failed to download package. Please try again.')
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
    gap: 0.5rem;
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

/* Analysis Modal - Bottom Right */
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

/* 🔥 Issues Summary */
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

/* Success Banner */
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

/* Package Tags */
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

/* System Dependencies */
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

/* Dockerfile Preview */
.dockerfile-preview {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 12px;
    border-radius: 6px;
    font-family: monospace;
    font-size: 12px;
    overflow-x: auto;
    margin: 0;
}

/* Actions */
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

/* Slide Up Animation */
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
