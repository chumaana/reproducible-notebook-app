<template>
    <div class="auth-page">
        <div class="auth-card">
            <h2>Welcome Back</h2>
            <p class="subtitle">Sign in to access your R notebooks</p>
            <form @submit.prevent="handleSubmit" class="auth-form">
                <div class="form-group">
                    <label>Username or Email</label>
                    <input v-model="username" type="text" required placeholder="Enter your username" />
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input v-model="password" type="password" required placeholder="Enter your password" />
                </div>
                <div v-if="authStore.error" class="error-msg">
                    {{ authStore.error }}
                </div>
                <button type="submit" class="btn-primary" :disabled="authStore.loading">
                    {{ authStore.loading ? 'Signing in...' : 'Sign In' }}
                </button>
            </form>
            <div class="auth-footer">
                Don't have an account? <router-link to="/register">Create one</router-link>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
/**
 * Login page component.
 * Handles user authentication and redirects to the original requested page or notebooks list.
 */

import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'

const username = ref('')
const password = ref('')

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

/**
 * Handles login form submission.
 * Redirects to original page (if stored in query) or notebooks list on success.
 */
const handleSubmit = async () => {
    const success = await authStore.login({
        username: username.value,
        password: password.value,
    })

    if (success) {
        // Redirect to original page or notebooks list
        const redirect = route.query.redirect as string
        router.push(redirect || '/notebooks')
    }
}
</script>