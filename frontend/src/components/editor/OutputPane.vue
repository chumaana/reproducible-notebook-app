<template>
    <div class="output-pane">
        <div class="pane-header">
            <h3><i class="fas fa-file-alt"></i> Output</h3>
            <div class="output-status">
                <span v-if="isLoading" class="status-running">
                    <i class="fas fa-spinner fa-spin"></i> Processing...
                </span>
                <span v-else-if="executionError" class="status-error">
                    <i class="fas fa-times-circle"></i> Failed
                </span>
                <span v-else-if="saveError" class="status-error">
                    <i class="fas fa-exclamation-triangle"></i> Save Error
                </span>
                <span v-else-if="result" class="status-success">
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
                <pre class="error-details">{{ executionError }}</pre>
            </details>
        </div>

        <!-- ✅ Save Error -->
        <div v-else-if="saveError" class="output-save-error">
            <div class="error-banner save-error-banner">
                <i class="fas fa-floppy-disk"></i>
                <strong>Save Failed</strong>
            </div>
            <div class="highlighted-error">
                <h4><i class="fas fa-exclamation-circle"></i> Validation Error:</h4>
                <pre>{{ saveError }}</pre>
            </div>
            <div class="error-actions">
                <button @click="clearSaveError" class="btn btn-outline">
                    <i class="fas fa-sync"></i> Retry Save
                </button>
                <button @click="clearAllErrors" class="btn btn-secondary">
                    <i class="fas fa-times"></i> Dismiss
                </button>
            </div>
        </div>

        <div v-else-if="result" class="output-content">
            <iframe :srcdoc="result" class="output-iframe"></iframe>
        </div>

        <div v-else class="output-empty">
            <i class="fas fa-play-circle"></i>
            <p>Click "Run" to execute your notebook</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useNotebookStore } from '@/stores/notebookStore'
import { storeToRefs } from 'pinia';

const store = useNotebookStore()
const { saveError } = storeToRefs(store)

const props = defineProps<{
    result: string | null
    error: string | null
    isLoading: boolean
}>()

/**
 * True if there's an execution error (not save error)
 */
const executionError = computed(() => {
    return props.error && !saveError.value ? props.error : null
})

/**
 * Parse R execution errors for better display
 */
const parsedError = computed(() => {
    if (!executionError.value) return null

    const errorMatch = executionError.value.match(
        /(Error in[\s\S]+?Execution halted)|(Error:[\s\S]+)|(! cannot open[\s\S]+)/
    )
    if (errorMatch) {
        return errorMatch[0].trim()
    }

    const lines = executionError.value.split('\n')
    return lines.slice(-10).join('\n')
})

/**
 * Clear save error and retry
 */
const clearSaveError = () => {
    store.clearErrors()
}

/**
 * Clear all errors
 */
const clearAllErrors = () => {
    store.clearErrors()
}
</script>

<style scoped>
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
    flex-shrink: 0;
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

/* Execution Error */
.output-error {
    flex: 1;
    padding: 2rem;
    background: #fff5f5;
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

.output-save-error {
    flex: 1;
    padding: 2rem;
    background: #fff5f5;
    overflow-y: auto;
}

.save-error-banner {
    color: #991b1b;
}

.error-actions {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #fecaca;
    display: flex;
    gap: 1rem;
}

.btn {
    padding: 0.75rem 1.25rem;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
    border: none;
}

.btn-outline {
    background: white;
    border: 1px solid #fecaca;
    color: #991b1b;
}

.btn-outline:hover {
    background: #fee2e2;
}

.btn-secondary {
    background: #6b7280;
    color: white;
}

.btn-secondary:hover {
    background: #4b5563;
}

.full-log-details {
    margin-top: 1rem;
}

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
</style>
