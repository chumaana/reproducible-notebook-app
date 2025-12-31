<template>
    <header class="app-header">
        <nav class="navbar">
            <div class="container navbar-container">
                <RouterLink to="/" class="navbar-brand">
                    <div class="logo">
                        <div class="logo-face">
                            <span class="logo-eyes">RЯ</span>
                            <span class="logo-smile">~</span>
                        </div>
                    </div>
                </RouterLink>
                <button class="mobile-menu-toggle" :class="{ active: mobileMenuOpen }" @click="toggleMobileMenu"
                    aria-label="Toggle menu">
                    <i class="fas" :class="mobileMenuOpen ? 'fa-times' : 'fa-bars'"></i>
                </button>
                <div class="navbar-nav" :class="{ open: mobileMenuOpen }">
                    <RouterLink to="/" class="nav-link" @click="closeMobileMenu">
                        <i class="fas fa-home"></i>
                        <span>Home</span>
                    </RouterLink>
                    <!-- Notebooks link - shows different content based on auth -->
                    <RouterLink to="/notebooks" class="nav-link" @click="closeMobileMenu">
                        <i class="fas" :class="authStore.isAuthenticated ? 'fa-folder' : 'fa-globe'"></i>
                        <span>{{ authStore.isAuthenticated ? 'My Notebooks' : 'Public Notebooks' }}</span>
                    </RouterLink>
                    <RouterLink to="/help" class="nav-link" @click="closeMobileMenu">
                        <i class="fas fa-question-circle"></i>
                        <span>Help</span>
                    </RouterLink>
                    <div v-if="authStore.isAuthenticated" class="nav-user">
                        <RouterLink to="/profile" class="nav-link user-link" @click="closeMobileMenu">
                            <i class="fas fa-user-circle"></i>
                            <span>{{ authStore.user?.username }}</span>
                        </RouterLink>
                        <button @click="handleLogout" class="btn-logout" title="Sign Out" aria-label="Sign out">
                            <i class="fas fa-sign-out-alt"></i>
                            <span class="logout-text">Logout</span>
                        </button>
                    </div>
                    <div v-else class="nav-guest">
                        <RouterLink to="/login" class="nav-link" @click="closeMobileMenu">
                            Login
                        </RouterLink>
                        <RouterLink to="/register" class="btn-register" @click="closeMobileMenu">
                            <i class="fas fa-rocket"></i>
                            Get Started
                        </RouterLink>
                    </div>
                </div>
            </div>
        </nav>
    </header>
</template>

<script setup lang="ts">
/**
 * Main application header with navigation and authentication controls.
 * Includes responsive mobile menu and conditional rendering based on auth state.
 * The "Notebooks" link shows user's notebooks when logged in, or public notebooks when not logged in.
 */

import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
    mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
    mobileMenuOpen.value = false
}

const handleLogout = async () => {
    await authStore.logout()
    closeMobileMenu()
    await router.push('/login')
}
</script>