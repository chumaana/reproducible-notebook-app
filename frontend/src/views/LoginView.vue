<script setup lang="ts">
/**
 * LoginView Component.
 * * Provides the user interface for authenticating existing users.
 * Integrates with the Pinia AuthStore to manage session state and persistence.
 * Implements post-login redirection logic to improve user experience when 
 * accessing protected routes.
 */
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'

/** @type {import('vue').Ref<string>} Reactive reference for the login identifier */
const username = ref('')

/** @type {import('vue').Ref<string>} Reactive reference for the user password */
const password = ref('')

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

/**
 * Orchestrates the login workflow.
 * * 1. Invokes the global authStore login action.
 * 2. If successful, checks for a 'redirect' query parameter (set by the router guard).
 * 3. Navigates the user either to their intended destination or the default notebooks list.
 * * @returns {Promise<void>}
 */
const handleSubmit = async () => {
    const success = await authStore.login({
        username: username.value,
        password: password.value,
    })

    if (success) {
        // Retrieve the redirect path from URL query parameters (e.g., /login?redirect=/profile)
        const redirect = route.query.redirect as string

        // Ensure asynchronous navigation is completed before component unmount
        await router.push(redirect || '/notebooks')
    }
}
</script>

<template>
    <div class="auth-page">
        <div class="auth-card">
            <h2>Welcome Back</h2>
            <p class="subtitle">Sign in to access your R notebooks</p>



            <form @submit.prevent="handleSubmit" class="auth-form">
                <div class="form-group">
                    <label>Username or Email</label>
                    <input v-model="username" name="username" type="text" required placeholder="Enter your username" />
                </div>

                <div class="form-group">
                    <label>Password</label>
                    <input v-model="password" name="password" type="password" required
                        placeholder="Enter your password" />
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