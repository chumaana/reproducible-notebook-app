<script setup lang="ts">
/**
 * NotFoundView Component.
 * * Serves as the "Catch-all" fallback page for the application's routing system.
 * It is triggered whenever a user attempts to access a URL that does not 
 * match any defined path in the Vue Router configuration.
 * * Purpose:
 * - Provides immediate feedback for dead links or typos.
 * - Prevents the application from displaying a blank screen or broken UI.
 * - Guides the user back to the primary functional area (Home).
 */
import { RouterLink } from 'vue-router'
</script>

<template>
    <div class="not-found-page">
        <div class="container">
            <div class="not-found-content">
                <i class="fas fa-exclamation-triangle"></i>

                <h1>404</h1>
                <p>Page not found</p>

                <RouterLink to="/" class="btn btn-primary">
                    <i class="fas fa-home"></i>
                    Go Home
                </RouterLink>
            </div>
        </div>
    </div>
</template>

<style scoped>
/**
 * Layout styling for the 404 page.
 * Uses Flexbox to vertically and horizontally center the error content,
 * ensuring it remains legible and prominent on all screen sizes.
 */
.not-found-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-gray-50);
}

.not-found-content {
    text-align: center;
    padding: var(--space-12);
}

.not-found-content i {
    font-size: 5rem;
    color: var(--color-warning);
    margin-bottom: var(--space-4);
}

.not-found-content h1 {
    font-size: 6rem;
    font-weight: 800;
    color: var(--color-gray-800);
    margin: 0;
}

.not-found-content p {
    font-size: 1.25rem;
    color: var(--color-gray-600);
    margin-bottom: var(--space-6);
}
</style>