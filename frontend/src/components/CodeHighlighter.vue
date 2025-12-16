<template>
  <div class="code-highlighter">
    <div v-for="(line, idx) in lines" :key="idx"
         class="code-line"
         :class="getLineClass(idx + 1)"
         @mouseenter="hoveredLine = idx + 1"
         @mouseleave="hoveredLine = null">
      
      <!-- Line Number -->
      <span class="line-number">{{ idx + 1 }}</span>
      
      <!-- Code Content -->
      <span class="line-code">{{ line }}</span>
      
      <!-- Issue Indicator -->
      <span v-if="getIssueForLine(idx + 1)" class="issue-indicator">
        <i class="fas fa-exclamation-triangle"></i>
      </span>
      
      <!-- Tooltip on hover -->
      <div v-if="hoveredLine === idx + 1 && getIssueForLine(idx + 1)" 
           class="issue-tooltip">
        <strong>{{ getIssueForLine(idx + 1).title }}</strong>
        <p>{{ getIssueForLine(idx + 1).fix }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

const issuesByLine = computed(() => {
  const map = new Map()
  props.issues.forEach(issue => {
    issue.lines?.forEach(lineInfo => {
      map.set(lineInfo.line_number, issue)
    })
  })
  return map
})

function getLineClass(lineNum: number) {
  const issue = issuesByLine.value.get(lineNum)
  if (!issue) return ''
  
  return {
    'line-error': issue.severity === 'high',
    'line-warning': issue.severity === 'medium',
    'line-info': issue.severity === 'low'
  }
}

function getIssueForLine(lineNum: number) {
  return issuesByLine.value.get(lineNum)
}
</script>

<style scoped>
.code-highlighter {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 8px;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

.code-line {
  display: flex;
  align-items: center;
  padding: 2px 12px;
  position: relative;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}

.code-line:hover {
  background: rgba(255, 255, 255, 0.05);
}

.line-error {
  background: rgba(255, 100, 100, 0.1);
  border-left-color: #ff6464;
}

.line-warning {
  background: rgba(255, 200, 100, 0.1);
  border-left-color: #ffc864;
}

.line-info {
  background: rgba(100, 150, 255, 0.1);
  border-left-color: #6496ff;
}

.line-number {
  width: 40px;
  text-align: right;
  color: #858585;
  user-select: none;
  margin-right: 16px;
  flex-shrink: 0;
}

.line-code {
  flex: 1;
  white-space: pre;
}

.issue-indicator {
  margin-left: 8px;
  color: #ffc864;
  font-size: 12px;
}

.issue-tooltip {
  position: absolute;
  right: 50px;
  top: 0;
  width: 280px;
  background: #2d2d2d;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 12px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  pointer-events: none;
}

.issue-tooltip strong {
  display: block;
  color: #ffc864;
  margin-bottom: 6px;
  font-size: 13px;
}

.issue-tooltip p {
  margin: 0;
  color: #a0a0a0;
  font-size: 12px;
  line-height: 1.4;
}
</style>
