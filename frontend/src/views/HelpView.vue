<template>
  <div class="help-page">
    <div class="container">
      <!-- Header -->
      <div class="help-header">
        <h1><i class="fas fa-question-circle"></i> Help & Documentation</h1>
        <p>Learn how to use the R Notebook Editor</p>
      </div>

      <!-- Quick Links -->
      <div class="quick-links">
        <a href="#getting-started" class="quick-link">
          <i class="fas fa-rocket"></i>
          <span>Getting Started</span>
        </a>
        <a href="#editor" class="quick-link">
          <i class="fas fa-code"></i>
          <span>Editor Guide</span>
        </a>
        <a href="#reproducibility" class="quick-link">
          <i class="fas fa-box"></i>
          <span>Reproducibility</span>
        </a>
      </div>

      <!-- Getting Started -->
      <section id="getting-started" class="help-section">
        <h2><i class="fas fa-rocket"></i> Getting Started</h2>

        <div class="help-card">
          <h3>Creating Your First Notebook</h3>
          <ol>
            <li>Click <strong>"Create Notebook"</strong> from the home page</li>
            <li>Enter a title for your notebook in the header</li>
            <li>Write your R code in the editor</li>
            <li>Click <button class="btn btn-primary btn-inline"><i class="fas fa-save"></i> Save</button> to save your
              work</li>
          </ol>
        </div>
      </section>

      <!-- Using the Editor -->
      <section id="editor" class="help-section">
        <h2><i class="fas fa-code"></i> Editor Guide</h2>

        <div class="help-card">
          <h3>Interface Layout</h3>
          <p>The editor has two main panes:</p>
          <ul>
            <li><strong>Left:</strong> R Script editor with syntax highlighting</li>
            <li><strong>Right:</strong> Output display showing execution results</li>
          </ul>
          <p class="help-tip">
            <i class="fas fa-lightbulb"></i>
            Drag the resize handle between panes to adjust width
          </p>
        </div>

        <div class="help-card">
          <h3>Toolbar Buttons</h3>
          <div class="button-grid">
            <div class="button-demo">
              <button class="btn btn-primary"><i class="fas fa-save"></i> Save</button>
              <p>Saves your notebook (auto-saves every 2 seconds)</p>
            </div>

            <div class="button-demo">
              <button class="btn btn-success"><i class="fas fa-play"></i> Run</button>
              <p>Executes R code and displays output. Also runs static analysis.</p>
            </div>

            <div class="button-demo">
              <button class="btn btn-primary"><i class="fas fa-box"></i> Package</button>
              <p>Generates Docker package with R4R (must run code first)</p>
            </div>

            <div class="button-demo">
              <button class="btn btn-secondary"><i class="fas fa-code-compare"></i> Diff</button>
              <p>Compares local vs container output using RDiff</p>
            </div>

            <div class="button-demo">
              <button class="btn btn-outline"><i class="fas fa-chart-bar"></i> Analysis</button>
              <p>Shows reproducibility analysis panel</p>
            </div>

            <div class="button-demo">
              <button class="btn btn-outline"><i class="fas fa-download"></i> .Rmd</button>
              <p>Downloads as R Markdown file</p>
            </div>

            <div class="button-demo">
              <button class="btn btn-outline"><i class="fas fa-download"></i> Download</button>
              <p>Downloads Docker package ZIP</p>
            </div>
          </div>
        </div>

        <div class="help-card">
          <h3>Writing R Code</h3>
          <p>Your code is automatically wrapped in R Markdown format:</p>
          <pre><code>---
title: "Your Notebook Title"
output: html_document
---
```{r}
Your code here

library(ggplot2)
data <- mtcars
plot(data$wt, data$mpg)
```</code></pre>
        </div>
      </section>

      <!-- Reproducibility -->
      <section id="reproducibility" class="help-section">
        <h2><i class="fas fa-box"></i> Reproducibility Features</h2>

        <div class="help-card">
          <h3>Static Analysis</h3>
          <p>Automatic checks detect issues:</p>
          <ul>
            <li><strong>Hardcoded paths:</strong> <code>/home/user/data.csv</code></li>
            <li><strong>Missing random seeds:</strong> <code>sample()</code> without <code>set.seed()</code></li>
            <li><strong>Non-portable code:</strong> System-specific commands</li>
          </ul>
          <p class="help-tip">
            <i class="fas fa-exclamation-triangle"></i>
            Warnings appear in the editor header
          </p>
        </div>

        <div class="help-card">
          <h3>R4R Dependency Tracking</h3>
          <p>Automatically captures:</p>
          <ul>
            <li>R packages and exact versions</li>
            <li>System libraries (libcurl, libssl, etc.)</li>
            <li>OS information for Docker base image</li>
          </ul>
        </div>

        <div class="help-card">
          <h3>Complete Workflow</h3>
          <div class="workflow-steps-help">
            <div class="workflow-step-help">
              <div class="step-num">1</div>
              <div class="step-text">
                <strong>Run</strong>
                <p>Execute your code</p>
              </div>
            </div>
            <div class="workflow-arrow-help">→</div>
            <div class="workflow-step-help">
              <div class="step-num">2</div>
              <div class="step-text">
                <strong>Package</strong>
                <p>Generate Docker files</p>
              </div>
            </div>
            <div class="workflow-arrow-help">→</div>
            <div class="workflow-step-help">
              <div class="step-num">3</div>
              <div class="step-text">
                <strong>Diff</strong>
                <p>Validate outputs</p>
              </div>
            </div>
            <div class="workflow-arrow-help">→</div>
            <div class="workflow-step-help">
              <div class="step-num">4</div>
              <div class="step-text">
                <strong>Download</strong>
                <p>Get ZIP file</p>
              </div>
            </div>
          </div>
        </div>

        <div class="help-card">
          <h3>Docker Package Contents</h3>
          <p>The ZIP file includes:</p>
          <ul>
            <li><code>Dockerfile</code> - Docker build instructions</li>
            <li><code>Makefile</code> - Build automation</li>
            <li><code>manifest.json</code> - Dependency metadata</li>
            <li>Your R script and data files</li>
          </ul>
        </div>
      </section>


    </div>
  </div>
</template>
