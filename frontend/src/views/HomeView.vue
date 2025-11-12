<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <i class="fas fa-flask"></i>
          Reproducible R Notebook
        </h1>
        <p class="hero-description">
          Create and share reproducible R notebooks with automatic dependency detection using R4R
        </p>

        <div class="hero-actions">
          <RouterLink to="/notebook/new" class="btn btn-primary btn-lg">
            <i class="fas fa-plus"></i>
            Create New Notebook
          </RouterLink>
          <RouterLink to="/notebooks" class="btn btn-outline btn-lg">
            <i class="fas fa-folder-open"></i>
            Browse Notebooks
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2 class="features-title">Why Use Our Notebook Platform?</h2>

      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-sync-alt"></i>
          </div>
          <h3>Automatic Reproducibility</h3>
          <p>
            R4R integration automatically captures all dependencies, system libraries,
            and package versions needed to reproduce your results.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-code"></i>
          </div>
          <h3>Interactive Editor</h3>
          <p>
            Modern block-based editor with syntax highlighting for R code and
            markdown support for rich documentation.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <h3>Live Execution</h3>
          <p>
            Execute R code blocks directly in your browser and see results instantly
            with support for plots and visualizations.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-share-nodes"></i>
          </div>
          <h3>Easy Sharing</h3>
          <p>
            Export to R Markdown, PDF, HTML, or generate complete Docker environments
            for seamless collaboration.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-shield-alt"></i>
          </div>
          <h3>Best Practices</h3>
          <p>
            Real-time analysis checks for reproducibility issues like missing random
            seeds, hardcoded paths, and external dependencies.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="fab fa-docker"></i>
          </div>
          <h3>Docker Ready</h3>
          <p>
            Automatically generate Docker containers with complete execution environments
            for maximum portability and reproducibility.
          </p>
        </div>
      </div>
    </div>

    <div class="cta-section">
      <h2>Ready to get started?</h2>
      <p>Create your first reproducible R notebook in seconds</p>
      <RouterLink to="/notebook/new" class="btn btn-primary btn-lg">
        <i class="fas fa-rocket"></i>
        Start Creating
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.home-container {
  min-height: calc(100vh - 70px);
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--space-12) var(--space-6);
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: var(--space-4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
}

.hero-description {
  font-size: 1.25rem;
  margin-bottom: var(--space-8);
  opacity: 0.95;
}

.hero-actions {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  flex-wrap: wrap;
}

.btn-lg {
  padding: var(--space-4) var(--space-6);
  font-size: 1rem;
}

.features-section {
  padding: var(--space-12) var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.features-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-gray-800);
  margin-bottom: var(--space-10);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-6);
}

.feature-card {
  background: white;
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.feature-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin-bottom: var(--space-4);
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin-bottom: var(--space-2);
}

.feature-card p {
  color: var(--color-gray-600);
  line-height: 1.6;
}

.cta-section {
  background: var(--color-gray-100);
  padding: var(--space-12) var(--space-6);
  text-align: center;
}

.cta-section h2 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-gray-800);
  margin-bottom: var(--space-2);
}

.cta-section p {
  font-size: 1.125rem;
  color: var(--color-gray-600);
  margin-bottom: var(--space-6);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-description {
    font-size: 1rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
