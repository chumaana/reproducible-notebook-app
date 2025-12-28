<template>
    <div class="diff-modal" @click.stop>

        <div class="diff-modal-header">
            <h3><i class="fas fa-code-compare"></i> Semantic Diff (Local vs Container)</h3>
            <button @click="$emit('close')" class="modal-close-btn">
                <i class="fas fa-times"></i>
            </button>
        </div>

        <div class="diff-modal-body">

            <div v-if="!diffHtml" class="diff-empty">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading diff...</p>
            </div>

            <iframe v-else :srcdoc="diffHtml" class="diff-iframe"></iframe>

        </div>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    diffHtml: string | null
}>()

defineEmits(['close'])
</script>