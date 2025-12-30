<template>
    <div class="editor-actions">
        <button @click="$emit('save')" class="btn btn-primary " :disabled="isReadOnly">
            <i class="fas fa-save"></i> Save
        </button>
        <button @click="$emit('run')" class="btn btn-success" :disabled="isReadOnly || isExecuting">
            <i class="fas" :class="isExecuting ? 'fa-spinner fa-spin' : 'fa-play'"></i>
            {{ isExecuting ? 'Running...' : 'Run' }}
        </button>
        <button v-if="!canDownload" @click="$emit('generate')" class="btn btn-primary"
            :disabled="isReadOnly || isGenerating || !hasExecuted"
            :title="!hasExecuted ? 'Run notebook first' : 'Generate package'">
            <i class="fas" :class="isGenerating ? 'fa-spinner fa-spin' : 'fa-box'"></i>
            {{ isGenerating ? 'Building...' : 'Generate Package' }}
        </button>
        <button v-if="hasPackage && canDownload" @click="$emit('generate')" class="btn btn-primary"
            :disabled="isReadOnly || isGenerating">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isGenerating }"></i>
        </button>
        <button @click="$emit('diff')" class="btn btn-secondary" :disabled="isReadOnly || isDiffing || !canDiff">
            <i class="fas" :class="isDiffing ? 'fa-spinner fa-spin' : 'fa-code-compare'"></i>
            {{ isDiffing ? 'Comparing...' : 'Diff' }}
        </button>
        <button @click="$emit('toggleAnalysis')" class="btn btn-outline">
            <i class="fas fa-chart-bar"></i> Analysis
        </button>

        <button @click="$emit('downloadRmd')" class="btn btn-outline" title="Download .Rmd file"
            :disabled="isReadOnly">
            <i class="fas fa-download"></i>
            .Rmd
        </button>
        <button v-if="canDownload" @click="$emit('download')" class="btn btn-outline"
            :disabled="isReadOnly || isDownloading">
            <i class="fas" :class="isDownloading ? 'fa-spinner fa-spin' : 'fa-download'"></i>
            Download ZIP
        </button>
    </div>
</template>

<script setup lang="ts">
/**
 * Toolbar component for notebook editor actions.
 * Handles saving, execution, package generation, diff comparison, downloads, and sharing.
 */

defineProps<{
    isReadOnly?: boolean      //  Whether notebook is public and accessed by not owner
    isExecuting: boolean      // Code execution in progress
    isGenerating: boolean     // R4R package generation in progress
    isDiffing: boolean        // Diff comparison in progress
    isDownloading: boolean    // ZIP download in progress
    hasExecuted: boolean      // Whether notebook has been executed at least once
    hasPackage: boolean       // Whether R4R package has been generated
    canDiff: boolean          // Whether diff comparison is available
    canDownload: boolean      // Whether package is ready for download
    isPublic?: boolean        // Whether notebook is public
    notebookId?: number       // Notebook ID for sharing
}>()

defineEmits<{
    save: []
    run: []
    generate: []
    diff: []
    toggleAnalysis: []
    downloadRmd: []
    download: []
}>()
</script>