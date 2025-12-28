<template>
    <div class="auth-page">
        <div class="auth-card">
            <h2>Create Account</h2>
            <p class="subtitle">Start reproducible data science today</p>
            <form @submit.prevent="handleSubmit" class="auth-form">
                <div class="form-group">
                    <label>Username</label>
                    <input v-model="username" type="text" required />
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input v-model="email" type="email" required />
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input v-model="password" type="password" required />
                </div>
                <div class="form-group">
                    <label>Confirm Password</label>
                    <input v-model="rePassword" type="password" required />
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

<script setup lang="ts">
/**
 * Registration page component.
 * Handles user account creation with password confirmation and automatic login after registration.
 */

import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const username = ref('')
const email = ref('')
const password = ref('')
const rePassword = ref('')
const localError = ref('')

const authStore = useAuthStore()
const router = useRouter()

// Display either local validation error or auth store error
const errorMessage = computed(() => localError.value || authStore.error)

/**
 * Handles registration form submission.
 * Validates password match, registers user, and logs in automatically on success.
 */
const handleSubmit = async () => {
    localError.value = ''
    authStore.clearError()

    // Validate passwords match
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
        // If backend auto-logs in, redirect directly
        if (authStore.isAuthenticated) {
            router.push('/notebooks')
        } else {
            // Otherwise, login manually then redirect
            await authStore.login({
                username: username.value,
                password: password.value
            })
            router.push('/notebooks')
        }
    }
}
</script>