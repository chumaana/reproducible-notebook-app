<template>
    <div class="main-content">
        <div class="notebook-editor">
            <div class="editor-header">
                <div class="title-section">
                    <input v-model="notebook.title" @blur="saveNotebook" class="notebook-title"
                        placeholder="Untitled Notebook">
                    <span class="author-info" v-if="notebook.author">
                        by {{ notebook.author }} • Last edited {{ formattedDate }}
                    </span>
                </div>

                <div class="editor-actions">
                    <button @click="addBlock('code')" class="btn btn-secondary">
                        <i class="fas fa-code"></i>
                        Add Code
                    </button>
                    <button @click="addBlock('markdown')" class="btn btn-outline">
                        <i class="fas fa-paragraph"></i>
                        Add Text
                    </button>
                    <button @click="executeAll" class="btn btn-success" :disabled="executing">
                        <i class="fas fa-play"></i>
                        {{ executing ? 'Running...' : 'Run All' }}
                    </button>
                    <button @click="saveNotebook" class="btn btn-primary">
                        <i class="fas fa-save"></i>
                        Save
                    </button>
                </div>
            </div>

            <!-- Notebook Blocks -->
            <div class="notebook-blocks">
                <div v-for="(block, index) in notebook.blocks" :key="block.id" class="notebook-block"
                    :class="{ 'block-code': block.block_type === 'code', 'block-markdown': block.block_type === 'markdown' }">
                    <!-- Block Header -->
                    <div class="block-header">
                        <div class="block-info">
                            <span class="block-type">
                                {{ block.block_type === 'code' ? 'R Code' : 'Markdown' }}
                            </span>
                            <span class="block-number" v-if="block.block_type === 'code'">
                                [{{ index + 1 }}]
                            </span>
                            <span v-if="block.executing" class="execution-status status-running">
                                <i class="fas fa-spinner fa-spin"></i>
                                Running...
                            </span>
                        </div>
                        <div class="block-actions">
                            <button v-if="block.block_type === 'code'" @click="executeBlock(block)" class="btn-icon"
                                :disabled="block.executing" title="Run block">
                                <i class="fas fa-play"></i>
                            </button>
                            <button @click="moveBlock(index, -1)" :disabled="index === 0" class="btn-icon"
                                title="Move up">
                                <i class="fas fa-arrow-up"></i>
                            </button>
                            <button @click="moveBlock(index, 1)" :disabled="index === notebook.blocks.length - 1"
                                class="btn-icon" title="Move down">
                                <i class="fas fa-arrow-down"></i>
                            </button>
                            <button @click="deleteBlock(block.id!)" class="btn-icon btn-danger" title="Delete block">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>

                    <div class="block-content">
                        <textarea v-model="block.content" @blur="updateBlock(block)"
                            :class="block.block_type === 'code' ? 'code-editor' : 'markdown-editor'"
                            :placeholder="block.block_type === 'code' ? 'Enter R code...' : 'Enter markdown text...'"
                            rows="8"></textarea>
                    </div>

                    <div v-if="block.block_type === 'code' && block.output" class="block-output">
                        <div class="output-header">
                            <span>Output</span>
                            <div class="output-actions">
                                <button class="btn-icon" title="Copy output">
                                    <i class="fas fa-copy"></i>
                                </button>
                                <button @click="block.output = ''" class="btn-icon" title="Clear output">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        </div>
                        <div class="output-content">
                            <pre class="output-text">{{ block.output }}</pre>
                        </div>
                    </div>
                </div>

                <div class="add-block-section">
                    <button class="btn-add-block">
                        <i class="fas fa-plus"></i>
                        Add Block
                    </button>
                    <div class="add-block-options">
                        <button @click="addBlock('code')" class="btn btn-sm">
                            <i class="fas fa-code"></i>
                            Code
                        </button>
                        <button @click="addBlock('markdown')" class="btn btn-sm">
                            <i class="fas fa-paragraph"></i>
                            Text
                        </button>
                    </div>
                </div>

                <div v-if="!notebook.blocks || notebook.blocks.length === 0" class="empty-notebook">
                    <h3>Start your notebook</h3>
                    <p>Add your first block to get started</p>
                    <div class="empty-actions">
                        <button @click="addBlock('code')" class="btn btn-primary btn-lg">
                            <i class="fas fa-code"></i>
                            Add Code Block
                        </button>
                        <button @click="addBlock('markdown')" class="btn btn-secondary btn-lg">
                            <i class="fas fa-paragraph"></i>
                            Add Text Block
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <aside class="sidebar">
            <div class="sidebar-section">
                <h3>
                    <i class="fas fa-check-circle"></i>
                    Reproducibility Status
                </h3>

                <div class="status-card status-good">
                    <div class="status-header">
                        <i class="fas fa-shield-alt"></i>
                        <span>Good</span>
                        <span class="status-score">85%</span>
                    </div>
                    <p>Your notebook follows most reproducibility best practices.</p>
                </div>

                <div class="checks-list">
                    <div class="check-item check-pass">
                        <i class="fas fa-check"></i>
                        <span>Random seed set</span>
                    </div>
                    <div class="check-item check-pass">
                        <i class="fas fa-check"></i>
                        <span>Libraries loaded</span>
                    </div>
                    <div class="check-item check-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>External data sources</span>
                    </div>
                    <div class="check-item check-pass">
                        <i class="fas fa-check"></i>
                        <span>No hardcoded paths</span>
                    </div>
                </div>
            </div>

            <div class="sidebar-section">
                <h3>
                    <i class="fas fa-cogs"></i>
                    R4R Analysis
                </h3>

                <div class="r4r-status">
                    <div class="r4r-item">
                        <span class="r4r-label">Dependencies:</span>
                        <span class="r4r-value">5 packages</span>
                    </div>
                    <div class="r4r-item">
                        <span class="r4r-label">System libs:</span>
                        <span class="r4r-value">3 detected</span>
                    </div>
                    <div class="r4r-item">
                        <span class="r4r-label">Docker ready:</span>
                        <span class="r4r-value status-ready">Yes</span>
                    </div>
                </div>

                <button class="btn btn-primary btn-full">
                    <i class="fas fa-download"></i>
                    Generate Environment
                </button>
            </div>

            <div class="sidebar-section">
                <h3>
                    <i class="fas fa-share-alt"></i>
                    Export & Share
                </h3>

                <div class="export-options">
                    <button class="btn btn-outline btn-sm">
                        <i class="fas fa-file-code"></i>
                        R Markdown
                    </button>
                    <button class="btn btn-outline btn-sm">
                        <i class="fas fa-file-pdf"></i>
                        PDF
                    </button>
                    <button class="btn btn-outline btn-sm">
                        <i class="fas fa-globe"></i>
                        HTML
                    </button>
                    <button class="btn btn-outline btn-sm">
                        <i class="fab fa-docker"></i>
                        Docker
                    </button>
                </div>
            </div>
        </aside>

        <div v-if="loading" class="loading-overlay">
            <div class="spinner"></div>
            <p>Loading notebook...</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { type Notebook, type NotebookBlock } from '@/services/api'

const route = useRoute()
const router = useRouter()

const notebook = ref<Notebook>({
    title: 'Untitled Notebook',
    blocks: []
})
const loading = ref(false)
const executing = ref(false)

const formattedDate = computed(() => {
    if (!notebook.value.updated_at) return ''
    const date = new Date(notebook.value.updated_at)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))

    if (hours < 1) return 'just now'
    if (hours < 24) return `${hours} hours ago`
    return date.toLocaleDateString()
})

const loadNotebook = async () => {
    const notebookId = route.params.id as string

    if (notebookId && notebookId !== 'new') {
        loading.value = true
        try {
            notebook.value = await api.getNotebook(notebookId)
        } catch (error) {
            console.error('Error loading notebook:', error)
            await createNotebook()
        }
        loading.value = false
    } else {
        await createNotebook()
    }
}

const createNotebook = async () => {
    try {
        const newNotebook = await api.createNotebook({
            title: notebook.value.title
        })
        notebook.value = newNotebook
        router.replace(`/notebook/${newNotebook.id}`)
    } catch (error) {
        console.error('Error creating notebook:', error)
    }
}

const saveNotebook = async () => {
    if (!notebook.value.id) return

    try {
        await api.updateNotebook(notebook.value.id, {
            title: notebook.value.title
        })
    } catch (error) {
        console.error('Error saving notebook:', error)
    }
}

const addBlock = async (blockType: 'code' | 'markdown') => {
    if (!notebook.value.id) return

    try {
        const response = await fetch(`http://localhost:8000/api/notebooks/${notebook.value.id}/add_block/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ block_type: blockType })
        })

        const newBlock = await response.json()
        if (notebook.value.blocks) {
            notebook.value.blocks.push(newBlock)
        } else {
            notebook.value.blocks = [newBlock]
        }
    } catch (error) {
        console.error('Error adding block:', error)
    }
}

const updateBlock = async (block: NotebookBlock) => {
    try {
        await api.updateBlock(block.id!, { content: block.content })
    } catch (error) {
        console.error('Error updating block:', error)
    }
}

const executeBlock = async (block: NotebookBlock & { executing?: boolean }) => {
    if (!notebook.value.id) return

    block.executing = true
    try {
        const response = await fetch(`http://localhost:8000/api/notebooks/${notebook.value.id}/execute_block/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ block_id: block.id })
        })

        const updatedBlock = await response.json()

        const blockIndex = notebook.value.blocks?.findIndex(b => b.id === block.id)
        if (blockIndex !== -1 && notebook.value.blocks) {
            notebook.value.blocks[blockIndex] = updatedBlock
        }
    } catch (error) {
        console.error('Error executing block:', error)
    }
    block.executing = false
}

const executeAll = async () => {
    executing.value = true
    if (notebook.value.blocks) {
        for (const block of notebook.value.blocks) {
            if (block.block_type === 'code') {
                await executeBlock(block)
            }
        }
    }
    executing.value = false
}

const deleteBlock = async (blockId: string) => {
    if (!confirm('Are you sure you want to delete this block?')) return

    try {
        await api.deleteBlock(blockId)
        if (notebook.value.blocks) {
            notebook.value.blocks = notebook.value.blocks.filter(b => b.id !== blockId)
        }
    } catch (error) {
        console.error('Error deleting block:', error)
    }
}

const moveBlock = async (index: number, direction: number) => {
    if (!notebook.value.blocks) return

    const newIndex = index + direction
    if (newIndex >= 0 && newIndex < notebook.value.blocks.length) {
        const blocks = [...notebook.value.blocks]
        const temp = blocks[index]
        blocks[index] = blocks[newIndex]
        blocks[newIndex] = temp

        blocks[index].order = index
        blocks[newIndex].order = newIndex

        notebook.value.blocks = blocks

        await updateBlock(blocks[index])
        await updateBlock(blocks[newIndex])
    }
}

onMounted(() => {
    loadNotebook()
})
</script>

<style scoped>
.main-content {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: var(--space-6);
    padding: var(--space-6);
    max-width: 1400px;
    margin: 0 auto;
}

.notebook-editor {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
}

.editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-6);
    border-bottom: 1px solid var(--color-gray-200);
    background: var(--color-gray-50);
}

.title-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
}

.notebook-title {
    font-size: 1.5rem;
    font-weight: 600;
    border: none;
    background: transparent;
    color: var(--color-gray-900);
    padding: var(--space-1) 0;
    min-width: 300px;
}

.notebook-title:focus {
    outline: none;
    border-bottom: 2px solid var(--color-primary);
}

.author-info {
    font-size: 0.875rem;
    color: var(--color-gray-500);
}

.editor-actions {
    display: flex;
    gap: var(--space-2);
}

.notebook-blocks {
    padding: var(--space-6);
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
}

.notebook-block {
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    overflow: hidden;
    background: white;
    box-shadow: var(--shadow-sm);
}

.block-code {
    border-left: 4px solid var(--color-primary);
}

.block-markdown {
    border-left: 4px solid var(--color-secondary);
}

.block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-3) var(--space-4);
    background: var(--color-gray-50);
    border-bottom: 1px solid var(--color-gray-200);
}

.block-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.block-type {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--color-gray-600);
}

.block-number {
    font-size: 0.75rem;
    color: var(--color-gray-500);
    font-family: var(--font-mono);
}

.execution-status {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.75rem;
    font-weight: 500;
}

.status-running {
    color: var(--color-warning);
}

.block-actions {
    display: flex;
    gap: var(--space-1);
}

.block-content {
    padding: 0;
}

.code-editor,
.markdown-editor {
    width: 100%;
    border: none;
    outline: none;
    padding: var(--space-4);
    font-family: var(--font-mono);
    font-size: 14px;
    line-height: 1.5;
    background: #1e293b;
    color: #e2e8f0;
    resize: vertical;
}

.markdown-editor {
    background: var(--color-gray-50);
    color: var(--color-gray-800);
    font-family: var(--font-sans);
}

.code-editor:focus {
    background: #0f172a;
}

.markdown-editor:focus {
    background: white;
}

.block-output {
    border-top: 1px solid var(--color-gray-200);
}

.output-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-2) var(--space-4);
    background: #334155;
    color: #cbd5e1;
    font-size: 0.75rem;
    font-weight: 600;
}

.output-actions {
    display: flex;
    gap: var(--space-1);
}

.output-content {
    padding: var(--space-4);
    background: #1e293b;
}

.output-text {
    color: #22c55e;
    font-family: var(--font-mono);
    font-size: 0.8rem;
    white-space: pre-wrap;
    margin: 0;
}

.add-block-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-4);
    border: 2px dashed var(--color-gray-300);
    border-radius: var(--radius-lg);
    background: var(--color-gray-50);
}

.btn-add-block {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
    background: white;
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    color: var(--color-gray-600);
    cursor: pointer;
    transition: all 0.2s;
}

.btn-add-block:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
}

.add-block-options {
    display: flex;
    gap: var(--space-2);
}

.empty-notebook {
    text-align: center;
    padding: var(--space-12);
    color: var(--color-gray-600);
}

.empty-notebook h3 {
    margin-bottom: var(--space-2);
}

.empty-notebook p {
    margin-bottom: var(--space-6);
}

.empty-actions {
    display: flex;
    gap: var(--space-4);
    justify-content: center;
}

.sidebar {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
}

.sidebar-section {
    background: white;
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    box-shadow: var(--shadow-sm);
}

.sidebar-section h3 {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-gray-800);
    margin-bottom: var(--space-4);
}

.status-card {
    padding: var(--space-4);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-4);
}

.status-good {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.2);
}

.status-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
}

.status-score {
    margin-left: auto;
    font-weight: 700;
    color: var(--color-success);
}

.checks-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.check-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
}

.check-pass {
    color: var(--color-success);
}

.check-warning {
    color: var(--color-warning);
}

.r4r-status {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    margin-bottom: var(--space-4);
}

.r4r-item {
    display: flex;
    justify-content: space-between;
    font-size: 0.875rem;
}

.r4r-label {
    color: var(--color-gray-600);
}

.r4r-value {
    font-weight: 500;
}

.status-ready {
    color: var(--color-success);
}

.export-options {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-2);
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--color-gray-200);
    border-left-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@media (max-width: 1024px) {
    .main-content {
        grid-template-columns: 1fr;
    }

    .sidebar {
        order: -1;
    }
}

@media (max-width: 768px) {
    .editor-header {
        flex-direction: column;
        gap: var(--space-4);
        align-items: stretch;
    }

    .editor-actions {
        justify-content: center;
        flex-wrap: wrap;
    }

    .main-content {
        padding: var(--space-4);
    }
}
</style>
