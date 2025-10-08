<template>
  <div id="app">
    <nav class="navbar">
      <div class="container flex items-center justify-between py-4">
        <RouterLink to="/" class="navbar-brand">
          {{ appTitle }}
        </RouterLink>

        <div class="navbar-nav flex items-center gap-6">
          <RouterLink to="/" class="nav-link">Home</RouterLink>
          <RouterLink to="/notebooks" class="nav-link">Notebooks</RouterLink>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

const appTitle = import.meta.env.VITE_APP_TITLE || 'R Notebook'
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background-color: var(--color-primary);
  color: white;
  box-shadow: var(--shadow-md);
}

.navbar-brand {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  text-decoration: none;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-weight: 500;

  &:hover {
    color: white;
  }

  &.router-link-active {
    color: white;
    font-weight: 600;
  }
}

.main-content {
  flex: 1;
}
</style>
