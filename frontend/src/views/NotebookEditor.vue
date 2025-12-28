<template>
    <div class="notebook-editor">

        <div class="editor-header">
            <input v-model="notebookTitle" @blur="handleSave" class="notebook-title" placeholder="Untitled Notebook">

            <EditorToolbar :is-executing="executing" :is-generating="packageGenerating" :is-diffing="diffGenerating"
                :is-downloading="packageLoading" :has-executed="hasExecuted" :has-package="hasPackage"
                :can-diff="canGenerateDiff" :can-download="canDownloadPackage" @save="handleSave" @run="store.runLocal"
                @generate="store.runPackage" @diff="handleDiff" @toggleAnalysis="showAnalysis = true"
                @downloadRmd="downloadRmd" @download="store.downloadPackage" />
        </div>

        <div class="editor-split-view">

            <div class="editor-pane">
                <div class="pane-header">
                    <h3><i class="fas fa-code"></i> R Script</h3>

                    <div class="editor-status">
                        <span v-if="warnings.length > 0" class="warning-badge" @click="showAnalysis = true"
                            style="cursor: pointer;">
                            <i class="fas fa-exclamation-triangle"></i> {{ warnings.length }} warnings
                        </span>
                    </div>
                </div>

                <textarea ref="editorTextarea" v-model="cleanContent" @input="debouncedSave" class="rmarkdown-editor"
                    :placeholder="placeholderText" :class="{ 'has-warnings': warnings.length > 0 }"></textarea>
            </div>

            <div class="resize-handle" @mousedown="startResize"></div>

            <div class="output-pane">
                <OutputPane :result="executionResult" :error="executionError" :is-loading="executing" />
            </div>
        </div>

        <Transition name="slide-up">
            <AnalysisDrawer v-if="showAnalysis && (analysis || staticAnalysis)" :issues="adjustedIssues"
                :code="cleanContent" :diff-result="diffResult" :package-loading="packageLoading"
                :has-static-analysis="!!staticAnalysis" @close="showAnalysis = false" @openDiff="showDiffModal = true"
                @download="store.downloadPackage" />
        </Transition>

        <Transition name="fade">
            <div v-if="showDiffModal" class="modal-overlay" @click="showDiffModal = false">
                <DiffModal :diff-html="diffResult" @close="showDiffModal = false" />
            </div>
        </Transition>

    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useNotebookStore } from '@/stores/notebookStore'
import { useMarkdown } from '@/composables/useMarkdown' // <--- The wrapper logic

// Components
import EditorToolbar from '@/components/editor/EditorToolbar.vue'
import OutputPane from '@/components/editor/OutputPane.vue'
import AnalysisDrawer from '@/components/analysis/AnalysisDrawer.vue' // Assumption: You created this
import DiffModal from '@/components/analysis/DiffModal.vue'         // Assumption: You created this

const route = useRoute()
const store = useNotebookStore()
const {
    notebook, executing, executionResult, executionError,
    packageGenerating, diffGenerating, packageLoading,
    hasExecuted, hasPackage, canGenerateDiff, canDownloadPackage,
    warnings, analysis, diffResult, staticAnalysis, downloadPackage
} = storeToRefs(store)

const notebookTitle = ref('Untitled Notebook')
const cleanContent = ref('')
const showAnalysis = ref(false)
const showDiffModal = ref(false)
const paneWidth = ref(600)
const placeholderText = `# Write your R code here...`

const { extractCleanContent, generateFullRmd } = useMarkdown(notebookTitle, cleanContent)

watch(diffResult, (newVal) => {
    console.log("PARENT (View) received diffResult:", newVal)
})


onMounted(async () => {
    const id = route.params.id as string
    if (id && id !== 'new') {
        await store.load(id)
    } else {
        store.resetState()
    }

    notebookTitle.value = store.notebook.title || 'Untitled Notebook'
    cleanContent.value = extractCleanContent(store.notebook.content)
})

watch([cleanContent, notebookTitle], () => {
    store.notebook.content = generateFullRmd()
    store.notebook.title = notebookTitle.value
})

const handleSave = async () => {
    await store.save()
}

const debouncedSave = debounce(() => handleSave(), 2000)
const handleDiff = async () => {
    await store.runDiff()
    console.log("PARENT after runDiff:", diffResult.value)
    if (diffResult.value) {
        showDiffModal.value = true
    }
}

const downloadRmd = () => {
    const fullContent = generateFullRmd()
    const blob = new Blob([fullContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${notebookTitle.value}.Rmd`
    a.click()
    URL.revokeObjectURL(url)
}

const startResize = (e: MouseEvent) => {
    const startX = e.clientX
    const startWidth = paneWidth.value
    const onMove = (e: MouseEvent) => {
        const newWidth = startWidth + (e.clientX - startX)
        if (newWidth > 200 && newWidth < window.innerWidth - 300) {
            paneWidth.value = newWidth
        }
    }
    const onUp = () => {
        document.removeEventListener('mousemove', onMove)
        document.removeEventListener('mouseup', onUp)
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
}

function debounce(fn: Function, delay: number) {
    let timeout: any
    return (...args: any[]) => {
        clearTimeout(timeout)
        timeout = setTimeout(() => fn(...args), delay)
    }
}
const adjustedIssues = computed(() => {
    return staticAnalysis.value?.issues || []
})
</script>