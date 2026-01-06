<template>
  <div class="code-highlighter">
    <div v-for="(line, idx) in lines" :key="idx" class="code-line" :class="getLineClass(idx + 1)"
      @mouseenter="hoveredLine = idx + 1" @mouseleave="hoveredLine = null">
      <span class="line-number">{{ idx + 1 }}</span>
      <span class="line-code">{{ line }}</span>
      <span v-if="getIssueForLine(idx + 1)" class="issue-indicator">
        <i class="fas fa-exclamation-triangle"></i>
      </span>
      <div v-if="hoveredLine === idx + 1 && getIssueForLine(idx + 1)" class="issue-tooltip">
        <strong>{{ getIssueForLine(idx + 1).title }}</strong>
        <p>{{ getIssueForLine(idx + 1).fix }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Displays code with line numbers and highlights lines containing reproducibility issues.
 * Shows issue tooltips on hover with severity-based styling.
 * 
 * Note: Backend analyzer returns line numbers relative to R code block (without YAML header).
 * We add RMARKDOWN_OFFSET to align with frontend display line numbers.
 */

import { computed, ref } from 'vue'

const props = defineProps<{
  code: string
  issues: Array<{
    title: string
    severity: string
    fix: string
    lines: Array<{ line_number: number, code: string }>
  }>
}>()

const hoveredLine = ref<number | null>(null)

const RMARKDOWN_OFFSET = 5

const lines = computed(() => props.code.split('\n'))

/**
 * Map line numbers to their associated issues.
 * Adjusts backend line numbers by adding RMARKDOWN_OFFSET to match frontend display.
 */
const issuesByLine = computed(() => {
  const map = new Map()
  props.issues.forEach(issue => {
    issue.lines?.forEach(lineInfo => {
      const frontendLineNum = lineInfo.line_number - RMARKDOWN_OFFSET
      map.set(frontendLineNum, issue)
    })
  })
  return map
})

/**
 * Returns CSS class based on issue severity.
 * 
 * @param lineNum - Frontend line number (1-indexed from start of file)
 * @returns Object with severity CSS class
 */
function getLineClass(lineNum: number) {
  const issue = issuesByLine.value.get(lineNum)
  if (!issue) return ''
  return {
    'line-error': issue.severity === 'high' || issue.severity === 'critical',
    'line-warning': issue.severity === 'medium',
    'line-info': issue.severity === 'low'
  }
}

/**
 * Gets the issue associated with a specific line number.
 * 
 * @param lineNum - Frontend line number (1-indexed)
 * @returns Issue object or undefined
 */
function getIssueForLine(lineNum: number) {
  return issuesByLine.value.get(lineNum)
}
</script>
