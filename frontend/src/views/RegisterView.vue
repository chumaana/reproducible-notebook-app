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

<style scoped>
.auth-page {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: #f3f4f6;
}

.auth-card {
    background: white;
    padding: 2.5rem;
    border-radius: 12px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
}

h2 {
    margin-top: 0;
    color: #111827;
    text-align: center;
}

.subtitle {
    color: #6b7280;
    text-align: center;
    margin-bottom: 2rem;
    font-size: 0.9rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
}

.form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    outline: none;
    transition: border 0.2s;
    box-sizing: border-box;
}

.form-group input:focus {
    border-color: #6366f1;
}

.btn-primary {
    width: 100%;
    padding: 0.75rem;
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 1rem;
}

.btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.error-msg {
    background: #fee2e2;
    color: #dc2626;
    padding: 0.75rem;
    border-radius: 6px;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

.auth-footer {
    margin-top: 1.5rem;
    text-align: center;
    font-size: 0.9rem;
    color: #6b7280;
}

.auth-footer a {
    color: #6366f1;
    text-decoration: none;
    font-weight: 600;
}
</style>