<template>
  <div id="app">
    <nav class="navbar">
      <div class="container navbar-container">
        <RouterLink to="/" class="navbar-brand">
          <i class="fas fa-notebook"></i>
          <span>R Notebook</span>
        </RouterLink>

        <div class="navbar-nav">

          <template v-if="authStore.isAuthenticated">
            <RouterLink to="/" class="nav-link">Home</RouterLink>
            <RouterLink to="/notebooks" class="nav-link">Notebooks</RouterLink>
          </template>

          <RouterLink to="/help" class="nav-link">Help</RouterLink>

          <div v-if="authStore.isAuthenticated" class="nav-user">
            <RouterLink to="/profile" class="nav-link">
              <div class="user-info">
                <i class="fas fa-user-circle"></i>
                <span>{{ authStore.user?.username }}</span>
              </div>
            </RouterLink>
            <button @click="handleLogout" class="btn-logout" title="Sign Out">
              <i class="fas fa-sign-out-alt"></i>
            </button>
          </div>

          <div v-else class="nav-guest">
            <RouterLink to="/login" class="nav-link">Login</RouterLink>
            <RouterLink to="/register" class="btn-register">Get Started</RouterLink>
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
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* --- Layout --- */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f9fafb;
  /* Light gray background for whole app */
}

/* --- Navbar --- */
.navbar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  /* Fixed height for consistency */
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #4f46e5;
  /* Indigo-600 */
  text-decoration: none;
}

.navbar-nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

/* --- Links --- */
.nav-link {
  color: #4b5563;
  /* Gray-600 */
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #4f46e5;
  font-weight: 600;
}

/* --- User Section --- */
.nav-user {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-left: 1rem;
  border-left: 1px solid #e5e7eb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #374151;
  font-weight: 600;
  font-size: 0.9rem;
}

.btn-logout {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  font-size: 1rem;
  padding: 5px;
  transition: color 0.2s;
}

.btn-logout:hover {
  color: #dc2626;
  /* Red on hover */
}

/* --- Guest Section --- */
.nav-guest {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-register {
  background-color: #4f46e5;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-register:hover {
  background-color: #4338ca;
}

main {
  flex: 1;
}

/* Mobile */
@media (max-width: 768px) {
  .navbar-container {
    flex-direction: column;
    height: auto;
    padding: 1rem;
    gap: 1rem;
  }

  .nav-user {
    border-left: none;
    padding-left: 0;
  }
}
</style>