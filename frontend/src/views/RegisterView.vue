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

                <div v-if="authStore.error" class="error-msg">
                    {{ authStore.error }}
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
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const username = ref('')
const email = ref('')
const password = ref('')
const rePassword = ref('')
const authStore = useAuthStore()
const router = useRouter()

const handleSubmit = async () => {
    if (password.value !== rePassword.value) {
        authStore.error = "Passwords do not match"
        return
    }

    const success = await authStore.register({
        username: username.value,
        email: email.value,
        password: password.value,
        password_confirm: rePassword.value
    })

    if (success) {
        await authStore.login({ username: username.value, password: password.value })
        router.push('/')
    }
}
</script>
