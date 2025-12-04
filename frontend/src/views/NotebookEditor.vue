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
            </div>
        </div>

        <!-- Split View: Editor | Output (like Overleaf) -->
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
                <textarea ref="editorTextarea" v-model="cleanContent" @input="debouncedSave" @scroll="onEditorScroll"
                    class="rmarkdown-editor" :placeholder="placeholderText"
                    :class="{ 'has-warnings': warnings.length > 0 }"></textarea>
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

        <!-- Analysis Modal -->
        <Transition name="modal">
            <div v-if="showAnalysis && analysis" class="modal-overlay" @click="showAnalysis = false">
                <div class="modal-container" @click.stop>
                    <div class="modal-header">
                        <h3><i class="fas fa-chart-bar"></i> R4R Analysis</h3>
                        <button @click="showAnalysis = false" class="modal-close" aria-label="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div class="modal-body">
                        <div class="analysis-item">
                            <span class="label">R4R Score:</span>
                            <span class="value score-badge">{{ analysis.r4r_score || 0 }}%</span>
                        </div>

                        <div class="analysis-item">
                            <span class="label">Dependencies:</span>
                            <span class="value">{{ (analysis.dependencies || []).length }} packages</span>
                        </div>

                        <div v-if="warnings.length > 0" class="warning-section">
                            <h4><i class="fas fa-exclamation-triangle text-warning"></i> Non-determinism Risks</h4>
                            <div class="warning-list">
                                <div v-for="warning in warnings.slice(0, 5)" :key="warning.line" class="warning-item">
                                    <i class="fas fa-bug text-warning"></i>
                                    <span class="warning-text">{{ warning.message }} (line {{ warning.line }})</span>
                                </div>
                                <div v-if="warnings.length > 5" class="warning-more">
                                    +{{ warnings.length - 5 }} more warnings
                                </div>
                            </div>
                        </div>

                        <div v-if="analysis.environments" class="comparison-section">
                            <h4><i class="fas fa-sync-alt"></i> Environment Diff</h4>
                            <div class="env-grid">
                                <div class="env-item" v-for="env in analysis.environments.slice(0, 2)" :key="env.name">
                                    <div class="env-name">{{ env.name }}</div>
                                    <div class="env-diff">{{ env.diff_score }}% match</div>
                                </div>
                            </div>
                        </div>

                        <div v-if="(analysis.dependencies || []).length > 0" class="section">
                            <h4>R Packages</h4>
                            <ul class="dependency-list">
                                <li v-for="dep in (analysis.dependencies || [])" :key="dep">
                                    <i class="fas fa-cube"></i> {{ dep }}
                                </li>
                            </ul>
                        </div>

                        <div class="action-section">
                            <h4><i class="fas fa-tools"></i> Quick Actions</h4>
                            <div class="action-buttons">
                                <button @click="generateDockerfile" class="btn btn-sm btn-secondary"
                                    :disabled="!analysis.dockerfile">
                                    Generate Reproducible Package
                                </button>

                                <button @click="shareReproducibility" class="btn btn-sm btn-outline">
                                    <i class="fas fa-share"></i> Share Report
                                </button>
                            </div>
                        </div>

                        <div v-if="analysis.dockerfile" class="section">
                            <h4>Dockerfile</h4>
                            <button @click="showDockerfile = !showDockerfile" class="btn btn-sm">
                                <i class="fas" :class="showDockerfile ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                                {{ showDockerfile ? 'Hide' : 'Show' }}
                            </button>
                            <pre v-if="showDockerfile" class="dockerfile-content">{{ analysis.dockerfile }}</pre>
                        </div>
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
const showAnalysis = ref(false)
const showDockerfile = ref(false)
const editorTextarea = ref<HTMLTextAreaElement | null>(null)

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
        console.log(result)
        executionResult.value = result.html

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
        warnings.value = data.warnings || []
        highlightWarnings()
    } catch (error) {
        console.error('Failed to load analysis:', error)
    }
}

const toggleAnalysis = async () => {
    if (!analysis.value || !notebook.value.id) {
        await loadAnalysis()
    } else {
        showAnalysis.value = !showAnalysis.value
    }
}

const highlightWarnings = () => {
    if (!editorTextarea.value || warnings.value.length === 0) return

    nextTick(() => {
        const textarea = editorTextarea.value
        const lines = textarea.value.split('\n')

        warnings.value.forEach(warning => {
            if (warning.line <= lines.length) {
                const lineElement = textarea.parentElement?.querySelector(
                    `[data-line="${warning.line}"]`
                ) as HTMLElement
                if (lineElement) {
                    lineElement.classList.add('warning-line')
                    lineElement.title = warning.message
                }
            }
        })
    })
}

const generateDockerfile = async () => {
    try {
        const response = await fetch(`/api/notebooks/${notebook.value.id}/docker/`, {
            method: 'POST'
        })
        const dockerData = await response.json()
        downloadFile(dockerData.dockerfile, 'Dockerfile', 'text/plain')
    } catch (error) {
        console.error('Docker generation failed:', error)
    }
}

const fixNonDeterminism = async () => {
    alert('Auto-fix feature coming soon!')
}

const shareReproducibility = () => {
    const reportUrl = `/report/${notebook.value.id}`
    navigator.clipboard.writeText(reportUrl)
    alert('Reproducibility report link copied!')
}

const downloadRmd = () => {
    const fullContent = generateFullRmd()
    downloadFile(fullContent, `${notebookTitle.value}.Rmd`, 'text/plain')
}

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

const onEditorScroll = () => {
    highlightWarnings()
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

.rmarkdown-editor.has-warnings {
    position: relative;
}

.rmarkdown-editor::placeholder {
    color: #9ca3af;
}

.warning-line {
    background: linear-gradient(90deg, rgba(254, 226, 226, 0.6) 0%, transparent 50%) !important;
    border-left: 4px solid #f87171;
    position: relative;
}

.warning-line::before {
    content: '⚠️';
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 12px;
    z-index: 10;
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

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

.modal-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow: hidden;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem 1rem 2rem;
    border-bottom: 1px solid #e5e7eb;
    background: #fafafa;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 700;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    color: #6b7280;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 6px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.modal-close:hover {
    background: #f3f4f6;
    color: #374151;
}

.modal-body {
    padding: 2rem;
    overflow-y: auto;
    max-height: calc(90vh - 80px);
}

.analysis-item {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid #f3f4f6;
}

.analysis-item .label {
    font-weight: 500;
    color: #6b7280;
    font-size: 0.875rem;
}

.analysis-item .value {
    font-weight: 600;
    color: #1f2937;
    font-size: 0.875rem;
}

.score-badge {
    background: #10b981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
}

.warning-section {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

.warning-list {
    max-height: 120px;
    overflow-y: auto;
}

.warning-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
    font-size: 0.85rem;
}

.warning-text {
    color: #92400e;
}

.warning-more {
    color: #d97706;
    font-size: 0.8rem;
    text-align: center;
    padding: 0.5rem;
    background: #fef3c7;
    border-radius: 4px;
    margin-top: 0.25rem;
}

.comparison-section {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

.env-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.env-item {
    padding: 1rem;
    background: white;
    border-radius: 6px;
    text-align: center;
}

.env-name {
    font-weight: 600;
    color: #0369a1;
    margin-bottom: 0.25rem;
}

.env-diff {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0ea5e9;
}

.section {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #f3f4f6;
}

.section h4 {
    margin: 0 0 0.75rem 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
}

.dependency-list {
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 0 0;
    max-height: 200px;
    overflow-y: auto;
}

.dependency-list li {
    padding: 0.5rem;
    margin: 0.25rem 0;
    background: #f9fafb;
    border-radius: 4px;
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.dependency-list li i {
    color: #6366f1;
}

.action-section {
    /* border-top: 1px solid #e5e7eb; */
    padding-top: 1rem;
    margin-bottom: 1rem;
}

.action-buttons {
    margin-top: 1rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.dockerfile-content {
    background: #1f2937;
    color: #f9fafb;
    padding: 0.75rem;
    border-radius: 4px;
    font-size: 0.7rem;
    line-height: 1.4;
    overflow-x: auto;
    margin-top: 0.5rem;
    max-height: 250px;
    overflow-y: auto;
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

.btn-warning {
    background: #f59e0b;
    color: white;
}

.btn-warning:hover:not(:disabled) {
    background: #d97706;
}

.btn-outline {
    background: white;
    border: 1px solid #d1d5db;
    color: #374151;
}

.btn-outline:hover {
    background: #f9fafb;
}

.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
}

.btn-icon {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    color: #6b7280;
}

.btn-icon:hover {
    color: #1f2937;
}

.text-warning {
    color: #f59e0b !important;
}

.modal-enter-active,
.modal-leave-active {
    transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}
</style>
