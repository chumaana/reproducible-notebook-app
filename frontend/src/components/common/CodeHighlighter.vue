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

const lines = computed(() => props.code.split('\n'))

// Map line numbers to their associated issues for quick lookup
const issuesByLine = computed(() => {
  const map = new Map()
  props.issues.forEach(issue => {
    issue.lines?.forEach(lineInfo => {
      map.set(lineInfo.line_number, issue)
    })
  })
  return map
})

/**
 * Returns CSS class based on issue severity.
 * 
 * @param lineNum - Line number to check
 * @returns Object with severity CSS class
 */
function getLineClass(lineNum: number) {
  const issue = issuesByLine.value.get(lineNum)
  if (!issue) return ''
  return {
    'line-error': issue.severity === 'high',
    'line-warning': issue.severity === 'medium',
    'line-info': issue.severity === 'low'
  }
}

/**
 * Gets the issue associated with a specific line number.
 * 
 * @param lineNum - Line number to check
 * @returns Issue object or undefined
 */
function getIssueForLine(lineNum: number) {
  return issuesByLine.value.get(lineNum)
}
</script>