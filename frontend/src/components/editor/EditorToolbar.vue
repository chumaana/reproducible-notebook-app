<template>
    <div class="editor-actions">
        <button @click="$emit('save')" class="btn btn-primary">
            <i class="fas fa-save"></i> Save
        </button>

        <button @click="$emit('run')" class="btn btn-success" :disabled="isExecuting">
            <i class="fas" :class="isExecuting ? 'fa-spinner fa-spin' : 'fa-play'"></i>
            {{ isExecuting ? 'Running...' : 'Run' }}
        </button>

        <button v-if="!canDownload" @click="$emit('generate')" class="btn btn-primary"
            :disabled="isGenerating || !hasExecuted" :title="!hasExecuted ? 'Run notebook first' : 'Generate package'">
            <i class="fas" :class="isGenerating ? 'fa-spinner fa-spin' : 'fa-box'"></i>
            {{ isGenerating ? 'Building...' : 'Generate Package' }}
        </button>

        <button v-if="hasPackage && canDownload" @click="$emit('generate')" class="btn btn-primary">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isGenerating }"></i>
        </button>

        <button @click="$emit('diff')" class="btn btn-secondary" :disabled="isDiffing || !canDiff">
            <i class="fas" :class="isDiffing ? 'fa-spinner fa-spin' : 'fa-code-compare'"></i>
            {{ isDiffing ? 'Comparing...' : 'Diff' }}
        </button>

        <button @click="$emit('toggleAnalysis')" class="btn btn-outline">
            <i class="fas fa-chart-bar"></i> Analysis
        </button>

        <button v-if="canDownload" @click="$emit('download')" class="btn btn-outline" :disabled="isDownloading">
            <i class="fas" :class="isDownloading ? 'fa-spinner fa-spin' : 'fa-download'"></i>
            Download ZIP
        </button>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    isExecuting: boolean;
    isGenerating: boolean;
    isDiffing: boolean;
    isDownloading: boolean;
    hasExecuted: boolean;
    hasPackage: boolean;
    canDiff: boolean;
    canDownload: boolean;
}>();

defineEmits(['save', 'run', 'generate', 'diff', 'toggleAnalysis', 'download']);
</script>