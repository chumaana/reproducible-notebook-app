<template>
    <footer class="app-footer">
        <div class="container footer-container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>R Notebook Editor</h3>
                    <p>Reproducible R notebooks with automatic dependency tracking.</p>
                </div>


                <div class="footer-section">
                    <h4>Resources</h4>
                    <ul class="footer-links">
                        <li><a href="https://github.com/chumaana/reproducible-notebook-app" target="_blank">GitHub</a>
                        </li>

                        <li><a href="https://r-tooling.github.io/" target="_blank">R4R Documentation</a></li>

                    </ul>
                </div>
            </div>

            <div class="footer-bottom">
                <p>&copy; {{ currentYear }} R Notebook Editor</p>
            </div>
        </div>
    </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-footer {
    background: white;
    border-top: 1px solid var(--color-gray-200);
    padding: 3rem 0 1.5rem;
    margin-top: auto;
}

.footer-container {
    max-width: 1200px;
}

.footer-content {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 3rem;
    margin-bottom: 1rem;
}

.footer-section h3 {
    color: var(--color-primary);
    font-size: 1.25rem;
    margin-bottom: 0.75rem;
}

.footer-section h4 {
    color: var(--color-gray-800);
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.footer-section p {
    color: var(--color-gray-600);
    line-height: 1.6;
    margin: 0;
}

.footer-links {
    list-style: none;
    padding: 0;
    margin: 0;
}

.footer-links li {
    margin-bottom: 0.5rem;
}

.footer-links a {
    color: var(--color-gray-600);
    text-decoration: none;
    font-size: 0.9375rem;
    transition: color 0.2s;
}

.footer-links a:hover {
    color: var(--color-primary);
}

.footer-bottom {
    text-align: center;
    padding-top: 2rem;
    border-top: 1px solid var(--color-gray-200);
}

.footer-bottom p {
    color: var(--color-gray-500);
    font-size: 0.875rem;
    margin: 0;
}

@media (max-width: 768px) {
    .footer-content {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
}
</style>
