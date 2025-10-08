<template>
  <div class="container py-8">
    <div class="text-center mb-12">
      <h1 class="text-2xl font-bold mb-4">
        Reproducible R Notebook
      </h1>
      <p class="text-lg text-gray-600 mb-8">
        Create and share reproducible R notebooks with automatic dependency detection
      </p>

      <div class="flex justify-center gap-4">
        <RouterLink to="/notebook/new" class="btn btn-primary btn-lg">
          Create New Notebook
        </RouterLink>
        <RouterLink to="/notebooks" class="btn btn-outline btn-lg">
          Browse Notebooks
        </RouterLink>
      </div>
    </div>

    <div class="grid-features">
      <div class="card">
        <div class="card-body text-center">
          <h3 class="font-semibold mb-2">Automatic Reproducibility</h3>
          <p class="text-gray-600">
            R4R integration automatically captures all dependencies
          </p>
        </div>
      </div>

      <div class="card">
        <div class="card-body text-center">
          <h3 class="font-semibold mb-2">Interactive Editor</h3>
          <p class="text-gray-600">
            Modern block-based editor for code and markdown
          </p>
        </div>
      </div>

      <div class="card">
        <div class="card-body text-center">
          <h3 class="font-semibold mb-2">Easy Sharing</h3>
          <p class="text-gray-600">
            Export to multiple formats with complete environments
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.grid-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-6);
  margin-top: var(--space-12);
}
</style>
