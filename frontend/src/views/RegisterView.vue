<script setup lang="ts">
/**
 * RegisterView Component.
 * * Provides the user interface for new account creation. 
 * This component manages the initial entry point for users into the 
 * reproducibility ecosystem, implementing:
 * 1. Client-side integrity checks (Password confirmation).
 * 2. Integration with the global Pinia AuthStore for registration logic.
 * 3. Automatic session establishment (auto-login) upon successful account creation.
 */

import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

/** @type {import('vue').Ref<string>} Reactive form field references */
const username = ref('')
const email = ref('')
const password = ref('')
const rePassword = ref('')

/** @type {import('vue').Ref<string>} Local validation error state (e.g., password mismatch) */
const localError = ref('')

const authStore = useAuthStore()
const router = useRouter()

/**
 * Error State Aggregation.
 * Computes the final error message by prioritizing local validation 
 * errors over server-side errors from the AuthStore.
 * @returns {string | null}
 */
const errorMessage = computed(() => localError.value || authStore.error)

/**
 * Registration Workflow Orchestrator.
 * * Process flow:
 * 1. Resets error states to ensure a clean attempt.
 * 2. Performs client-side validation (checks if password and rePassword match).
 * 3. Invokes the AuthStore's register action with user credentials.
 * 4. On success, ensures a token is present (auto-login) and redirects to the dashboard.
 * * @returns {Promise<void>}
 */
const handleSubmit = async () => {
    localError.value = ''
    authStore.clearError()

    // Client-side integrity check: ensure the user typed their password correctly twice
    if (password.value !== rePassword.value) {
        localError.value = 'Passwords do not match'
        return
    }

    const success = await authStore.register({
        username: username.value,
        email: email.value,
        password: password.value,
    })

    if (success) {
        // Post-registration redirect: move the user to their private workspace
        if (authStore.isAuthenticated) {
            router.push('/notebooks')
        } else {
            // Fallback: If the API doesn't return a token on register, perform a login attempt
            await authStore.login({
                username: username.value,
                password: password.value
            })
            router.push('/notebooks')
        }
    }
}
</script>

<template>
    <div class="auth-page">
        <div class="auth-card">
            <h2>Create Account</h2>
            <p class="subtitle">Start reproducible data science today</p>

            <form @submit.prevent="handleSubmit" class="auth-form">
                <div class="form-group">
                    <label>Username</label>
                    <input v-model="username" name="username" type="text" required />
                </div>

                <div class="form-group">
                    <label>Email</label>
                    <input v-model="email" name="email" type="email" required />
                </div>

                <div class="form-group">
                    <label>Password</label>
                    <input v-model="password" name="password" type="password" required />
                </div>

                <div class="form-group">
                    <label>Confirm Password</label>
                    <input v-model="rePassword" name="rePassword" type="password" required />
                </div>

                <div v-if="errorMessage" class="error-msg">
                    {{ errorMessage }}
                </div>

                <button type="submit" class="btn-primary" :disabled="authStore.loading">
                    {{ authStore.loading ? 'Creating account...' : 'Sign Up' }}
                </button>
            </form>

            <div class="auth-footer">
                Already have an account? <router-link to="/login">Sign In</router-link>
            </div>
        </div>
    </div>
</template>