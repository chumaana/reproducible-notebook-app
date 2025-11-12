<template>
  <div id="app">
    <nav class="navbar">
      <div class="container navbar-container">
        <RouterLink to="/" class="navbar-brand">
          <i class="fas fa-notebook"></i>
          <span>R Notebook</span>
        </RouterLink>

        <div class="navbar-nav">
          <RouterLink to="/" class="nav-link">Home</RouterLink>
          <RouterLink to="/notebooks" class="nav-link">Notebooks</RouterLink>
          <RouterLink to="/help" class="nav-link">Help</RouterLink>
          <div class="nav-user">
            <i class="fas fa-user-circle"></i>
            <span>User</span>
          </div>
        </div>
      </div>
    </nav>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: white;
  border-bottom: 1px solid var(--color-gray-200);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary);
  text-decoration: none;
}

.navbar-nav {
  display: flex;
  align-items: center;
  gap: var(--space-6);
}

.nav-link {
  color: var(--color-gray-600);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-gray-600);
  font-size: 0.875rem;
}

main {
  flex: 1;
}

@media (max-width: 768px) {
  .navbar-container {
    flex-direction: column;
    gap: var(--space-4);
  }
}
</style>
