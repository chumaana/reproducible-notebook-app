<template>
    <div class="analysis-modal-bottom">
        <div class="modal-header-bottom">
            <h3><i class="fas fa-chart-bar"></i> Reproducibility Analysis</h3>
            <button @click="$emit('close')" class="modal-close-btn" title="Close">
                <i class="fas fa-times"></i>
            </button>
        </div>

        <div class="modal-body-bottom">
            <div v-if="hasR4RData" class="section">
                <h4><i class="fab fa-docker"></i> Environment Metrics</h4>

                <div class="metrics-grid">
                    <div class="metric-card" :class="{ expanded: showAllPackages }">
                        <div class="card-header" @click="showAllPackages = !showAllPackages">
                            <div class="header-left">
                                <div class="icon-box r-icon"><i class="fas fa-cube"></i></div>
                                <div class="meta">
                                    <span class="count">{{ rPackages.length }}</span>
                                    <span class="label">R Packages</span>
                                </div>
                            </div>
                            <i class="fas fa-chevron-down toggle-icon"></i>
                        </div>

                        <div class="card-content">
                            <div class="package-tags">
                                <span v-for="pkg in visiblePackages" :key="pkg" class="package-tag" :title="pkg">
                                    {{ pkg }}
                                </span>
                                <button v-if="!showAllPackages && rPackages.length > 5"
                                    @click.stop="showAllPackages = true" class="show-more-btn">
                                    +{{ rPackages.length - 5 }} more
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="metric-card" :class="{ expanded: showAllSysLibs }">
                        <div class="card-header" @click="showAllSysLibs = !showAllSysLibs">
                            <div class="header-left">
                                <div class="icon-box sys-icon"><i class="fas fa-cogs"></i></div>
                                <div class="meta">
                                    <span class="count">{{ sysLibs.length }}</span>
                                    <span class="label">System Libs</span>
                                </div>
                            </div>
                            <i class="fas fa-chevron-down toggle-icon"></i>
                        </div>

                        <div class="card-content">
                            <div v-if="sysLibs.length === 0" class="empty-text">
                                No specific system dependencies detected.
                            </div>
                            <div v-else class="package-tags">
                                <span v-for="lib in visibleSysLibs" :key="lib" class="sys-dep-tag" :title="lib">
                                    {{ lib }}
                                </span>
                                <button v-if="!showAllSysLibs && sysLibs.length > 5" @click.stop="showAllSysLibs = true"
                                    class="show-more-btn">
                                    +{{ sysLibs.length - 5 }} more
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="issues.length > 0" class="section">
                <h4><i class="fas fa-exclamation-triangle"></i> Detected Issues</h4>
                <div class="issues-summary">
                    <div v-for="(issue, idx) in issues" :key="idx" class="issue-summary-card"
                        :class="`severity-${issue.severity}`">
                        <div class="issue-header">
                            <span class="severity-badge">{{ issue.severity }}</span>
                            <strong>{{ issue.title }}</strong>
                        </div>
                        <p class="issue-details">{{ issue.details }}</p>
                        <p v-if="issue.fix" class="issue-fix">💡 {{ issue.fix }}</p>

                        <span v-if="issue.lines && issue.lines.length" class="issue-count">
                            Line(s): {{ formatLines(issue.lines) }}
                        </span>
                    </div>
                </div>
            </div>

            <div v-if="issues.length > 0" class="section">
                <h4><i class="fas fa-code"></i> Context</h4>
                <CodeHighlighter :code="code" :issues="issues" />
            </div>

            <div v-if="issues.length === 0 && hasStaticAnalysis" class="section">
                <div class="success-banner">
                    <i class="fas fa-check-circle"></i> <span>No reproducibility issues detected!</span>
                </div>
            </div>

            <div class="modal-actions">
                <button v-if="diffResult" @click="$emit('openDiff')" class="btn btn-sm btn-secondary">
                    <i class="fas fa-code-compare"></i> View Semantic Diff
                </button>

                <button @click="$emit('download')" class="btn btn-sm btn-primary"
                    :disabled="packageLoading || isReadOnly">
                    <i class="fas" :class="packageLoading ? 'fa-spinner fa-spin' : 'fa-download'"></i>
                    {{ packageLoading ? 'Downloading...' : 'Download Reproducibility Package' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
/**
 * Drawer component for displaying reproducibility analysis results.
 * Shows R4R environment metrics, detected issues, and code context with issue highlighting.
 */

import { ref, computed, watchEffect } from 'vue'
import CodeHighlighter from '@/components/common/CodeHighlighter.vue'
import type { StaticAnalysisIssue, R4RData } from '@/types/index'

interface IssueLine {
    line_number: number
    code: string
}

const props = defineProps<{
    issues: StaticAnalysisIssue[]
    code: string
    diffResult?: string | null
    packageLoading: boolean
    hasStaticAnalysis: boolean
    r4rData?: R4RData | null
    isReadOnly?: boolean
}>()

defineEmits<{
    close: []
    openDiff: []
    download: []
}>()
watchEffect(() => {
    console.log('r4rData prop:', props.r4rData)
    console.log('r4rData type:', typeof props.r4rData)
    console.log('r4rData is array:', Array.isArray(props.r4rData))
})
const showAllPackages = ref(false)
const showAllSysLibs = ref(false)

const rPackages = computed(() => props.r4rData?.r_packages || [])
const sysLibs = computed(() => props.r4rData?.system_libs || [])

// Show first 5 items when collapsed, all when expanded
const visiblePackages = computed(() =>
    showAllPackages.value ? rPackages.value : rPackages.value.slice(0, 5)
)

const visibleSysLibs = computed(() =>
    showAllSysLibs.value ? sysLibs.value : sysLibs.value.slice(0, 5)
)

const hasR4RData = computed(() => {
    if (!props.r4rData || typeof props.r4rData !== 'object') return false
    return Object.keys(props.r4rData).length > 0
})


/**
 * Formats issue line numbers for display.
 * 
 * @param lines - Array of issue lines
 * @returns Comma-separated line numbers (e.g., "1, 2, 5")
 */
const formatLines = (lines: any[]) => {
    // Subtract 5 from each line number to account for the YAML header
    const RMARKDOWN_OFFSET = 5;

    return lines
        .map(line => line.line_number - RMARKDOWN_OFFSET)
        .join(', ');
}
</script>

<style scoped>
.metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 1rem;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.2s ease;
}

.metric-card.expanded {
    grid-column: 1 / -1;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.card-header {
    padding: 10px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    background: #f9fafb;
    border-bottom: 1px solid transparent;
}

.card-header:hover {
    background: #f3f4f6;
}

.metric-card.expanded .card-header {
    border-bottom-color: #e5e7eb;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 10px;
}

.icon-box {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 14px;
}

.r-icon {
    background: #6366f1;
}

.sys-icon {
    background: #8b5cf6;
}

.meta {
    display: flex;
    flex-direction: column;
    line-height: 1;
}

.count {
    font-weight: 700;
    font-size: 14px;
    color: #1f2937;
}

.label {
    font-size: 10px;
    color: #6b7280;
    text-transform: uppercase;
    margin-top: 2px;
    font-weight: 600;
}

.toggle-icon {
    color: #9ca3af;
    font-size: 12px;
    transition: transform 0.2s;
}

.expanded .toggle-icon {
    transform: rotate(180deg);
}

.card-content {
    padding: 12px;
}

.empty-text {
    font-size: 12px;
    color: #9ca3af;
    font-style: italic;
}

.show-more-btn {
    background: white;
    border: 1px dashed #d1d5db;
    color: #6b7280;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
}

.show-more-btn:hover {
    border-color: #6366f1;
    color: #6366f1;
}
</style>