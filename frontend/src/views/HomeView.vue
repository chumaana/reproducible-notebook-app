<script setup lang="ts">
/**
 * HomeView Component.
 * Serves as the primary landing page for the application.
 * Highlights the reproducibility-as-a-service value proposition, 
 * integrating key technical features like R4R dependency tracking, 
 * RDiff validation, and Docker containerization.
 */
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="home-container">
    <section class="hero">
      <div class="container">
        <div class="hero-content-center">
          <div class="hero-badge">
            <span class="badge-dot"></span>
            <span>Reproducible R Notebooks</span>
          </div>

          <h1>R Notebooks That<br />Actually Reproduce</h1>

          <p class="hero-lead">
            Web editor with automatic dependency tracking, static analysis,
            and Docker export. Write code that runs everywhere.
          </p>

          <div class="hero-cta">
            <RouterLink to="/notebook/new" class="btn-hero-primary">
              Create Notebook
              <i class="fas fa-arrow-right"></i>
            </RouterLink>
            <RouterLink to="/notebooks" class="btn-hero-secondary">
              <i class="fas fa-folder"></i>
              My Notebooks
            </RouterLink>
          </div>

          <div class="hero-features">
            <div class="hero-feature">
              <i class="fas fa-robot"></i>
              <span>R4R Powered</span>
            </div>
            <div class="hero-feature">
              <i class="fas fa-code-compare"></i>
              <span>RDiff Validation</span>
            </div>
            <div class="hero-feature">
              <i class="fab fa-docker"></i>
              <span>Docker Export</span>
            </div>
            <div class="hero-feature">
              <i class="fas fa-shield-alt"></i>
              <span>97.5% Success Rate</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="problem-solution">
      <div class="container">
        <h2>Stop Fighting with Dependencies</h2>

        <div class="comparison-grid">
          <div class="comparison-col problem">
            <h3>Traditional Notebooks</h3>
            <ul>
              <li>Code breaks when shared</li>
              <li>Missing package versions</li>
              <li>Hardcoded file paths</li>
              <li>Hours debugging environments</li>
            </ul>
          </div>

          <div class="comparison-col solution">
            <h3>This Tool</h3>
            <ul>
              <li>Dependencies tracked automatically</li>
              <li>Versions locked by R4R</li>
              <li>Static analysis warns about paths</li>
              <li>Docker export in one click</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="container">
        <h2>Write R Code. Get Reproducible Environment.</h2>
        <p class="section-subtitle">
          Web editor with automatic dependency tracking and Docker export
        </p>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-code"></i>
            </div>
            <h3>R Script Editor</h3>
            <p>
              Write and execute R code in your browser. Split-pane view
              shows code and HTML output side-by-side.
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-microscope"></i>
            </div>
            <h3>Static Analysis</h3>
            <p>
              Automatic checks for hardcoded paths, missing random seeds,
              and other reproducibility issues before you share.
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-robot"></i>
            </div>
            <h3>R4R Dependency Tracking</h3>
            <p>
              System-level tracing captures all packages, versions, and libraries.
              Validated on 120+ Kaggle notebooks.
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-code-compare"></i>
            </div>
            <h3>RDiff Validation</h3>
            <p>
              Semantic diff compares local vs container outputs.
              Verifies your code produces identical results.
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <i class="fab fa-docker"></i>
            </div>
            <h3>Docker Export</h3>
            <p>
              One-click generation of Dockerfile, Makefile, and manifest.
              Download complete package as ZIP.
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-download"></i>
            </div>
            <h3>R Markdown Export</h3>
            <p>
              Export to .Rmd format for use with RStudio, knitr,
              or other R Markdown tools.
            </p>
          </div>
        </div>

        <div class="tech-note">
          <p>
            <strong>Powered by research from CTU Prague:</strong>
            R4R for dependency detection, RDiff for semantic validation,
            and custom static analysis.
            <a href="https://r-tooling.github.io/" target="_blank">Learn more about R4R →</a>
          </p>
        </div>
      </div>
    </section>

    <section class="how-it-works">
      <div class="container">
        <h2>Your Workflow</h2>



        <div class="workflow-steps">
          <div class="workflow-step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>Write R Code</h3>
              <p>Use the web editor to write your analysis script</p>
            </div>
          </div>

          <div class="workflow-arrow">→</div>

          <div class="workflow-step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>Run & Check</h3>
              <p>Execute code and review static analysis warnings</p>
            </div>
          </div>

          <div class="workflow-arrow">→</div>

          <div class="workflow-step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>Generate Package</h3>
              <p>Create Docker environment with R4R</p>
            </div>
          </div>

          <div class="workflow-arrow">→</div>

          <div class="workflow-step">
            <div class="step-number">4</div>
            <div class="step-content">
              <h3>Validate with Diff</h3>
              <p>Compare outputs using RDiff</p>
            </div>
          </div>

          <div class="workflow-arrow">→</div>

          <div class="workflow-step">
            <div class="step-number">5</div>
            <div class="step-content">
              <h3>Download & Share</h3>
              <p>Get ZIP with Dockerfile or .Rmd</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="cta">
      <div class="container">
        <h2>Start Creating Reproducible Notebooks</h2>
        <p>No installation. No configuration. Just write R code.</p>
        <RouterLink to="/notebook/new" class="btn-cta">
          Create Your First Notebook
          <i class="fas fa-arrow-right"></i>
        </RouterLink>
      </div>
    </section>
  </div>
</template>