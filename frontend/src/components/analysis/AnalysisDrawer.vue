<template>
    <div class="analysis-modal-bottom">

        <div class="modal-header-bottom">
            <h3><i class="fas fa-chart-bar"></i> Reproducibility Analysis</h3>
            <button @click="$emit('close')" class="modal-close-btn">
                <i class="fas fa-times"></i>
            </button>
        </div>

        <div class="modal-body-bottom">

            <div v-if="issues.length > 0" class="section">
                <h4><i class="fas fa-exclamation-triangle"></i> Non-Reproducibility Issues</h4>
                <div class="issues-summary">
                    <div v-for="issue in issues" :key="issue.title" class="issue-summary-card"
                        :class="`severity-${issue.severity}`">
                        <div class="issue-header">
                            <span class="severity-badge">{{ issue.severity }}</span>
                            <strong>{{ issue.title }}</strong>
                        </div>
                        <p class="issue-details">{{ issue.details }}</p>
                        <p v-if="issue.fix" class="issue-fix">💡 {{ issue.fix }}</p>

                        <span v-if="issue.lines && issue.lines.length" class="issue-count">
                            Line(s): {{issue.lines.map((l: any) => l.line_number).join(',')}}
                        </span>
                    </div>
                </div>
            </div>

            <div v-if="issues.length > 0" class="section">
                <h4><i class="fas fa-code"></i> Code Context</h4>
                <CodeHighlighter :code="code" :issues="issues" />
            </div>

            <div v-if="issues.length === 0 && hasStaticAnalysis" class="section">
                <div class="success-banner">
                    <i class="fas fa-check-circle"></i> <span>No reproducibility issues detected!</span>
                </div>
            </div>

            <div class="modal-actions">
                <button v-if="diffResult" @click="$emit('openDiff')" class="btn btn-sm btn-secondary">
                    <i class="fas fa-code-compare"></i>
                    View Semantic Diff
                </button>

                <button @click="$emit('download')" class="btn btn-sm btn-primary" :disabled="packageLoading">
                    <i class="fas" :class="packageLoading ? 'fa-spinner fa-spin' : 'fa-download'"></i>
                    {{ packageLoading ? 'Downloading...' : 'Download Reproducibility Package' }}
                </button>
            </div>

        </div>
    </div>
</template>

<script setup lang="ts">
import CodeHighlighter from '@/components/common/CodeHighlighter.vue' // Adjust path if needed

defineProps<{
    issues: any[]        // Maps to 'adjustedIssues'
    code: string         // Maps to 'cleanContent'
    diffResult: string | null | undefined
    packageLoading: boolean
    hasStaticAnalysis: boolean // Maps to checking if 'staticAnalysis' exists
}>()

defineEmits(['close', 'openDiff', 'download'])
</script>