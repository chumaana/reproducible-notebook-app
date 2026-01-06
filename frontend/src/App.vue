<template>
  <div id="app">
    <AppHeader />
    <main class="main-content">
      <RouterView />
    </main>
    <AppFooter v-if="showFooter" />
  </div>
</template>

<script setup lang="ts">
/**
 * Root application component.
 * Provides main layout structure with header, content area, and conditional footer.
 */

import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'

const route = useRoute()

// Hide footer on editor page for full-height layout
const showFooter = computed(() => {
  return route.name !== 'notebook-editor'
})
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>