<template>
    <div class="output-pane">
        <div class="pane-header">
            <h3><i class="fas fa-file-alt"></i> Output</h3>
            <div class="output-status">
                <span v-if="isLoading" class="status-running">
                    <i class="fas fa-spinner fa-spin"></i> Processing...
                </span>
                <span v-else-if="error" class="status-error">
                    <i class="fas fa-times-circle"></i> Failed
                </span>
                <span v-else-if="result" class="status-success">
                    <i class="fas fa-check-circle"></i> Ready
                </span>
                <span v-else class="status-empty">
                    <i class="fas fa-info-circle"></i> Run to see output
                </span>
            </div>
        </div>
        <div v-if="error" class="output-error">
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
                <pre class="error-details">{{ error }}</pre>
            </details>
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
/**
 * Displays notebook execution output or errors.
 * Shows HTML results in iframe, parses R errors for user-friendly display.
 */

import { computed } from 'vue'

const props = defineProps<{
    result: string | null    // HTML output from successful execution
    error: string | null     // Error message from failed execution
    isLoading: boolean       // Execution in progress
}>()

/**
 * Extract meaningful error messages from R output.
 * Attempts to find R error patterns, falls back to last 10 lines.
 * 
 * @returns Parsed error string or null
 */
const parsedError = computed(() => {
    if (!props.error) return null

    // Try to find R error patterns
    const errorMatch = props.error.match(/(Error in[\s\S]+?Execution halted)|(Error:[\s\S]+)|(! cannot open[\s\S]+)/)
    if (errorMatch) {
        return errorMatch[0].trim()
    }

    // Fallback: show last 10 lines
    const lines = props.error.split('\n')
    return lines.slice(-10).join('\n')
})
</script>