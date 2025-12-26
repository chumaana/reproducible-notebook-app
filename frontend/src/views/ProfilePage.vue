<template>
    <div class="profile-page">
        <div class="profile-container">
            <div class="profile-header">
                <h1><i class="fas fa-user-circle"></i> My Profile</h1>
            </div>

            <div class="profile-card">
                <form @submit.prevent="saveProfile">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" v-model="profile.username" disabled class="form-input disabled" />
                        <small>Username cannot be changed</small>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>First Name</label>
                            <input type="text" v-model="profile.first_name" class="form-input" :disabled="!editing" />
                        </div>

                        <div class="form-group">
                            <label>Last Name</label>
                            <input type="text" v-model="profile.last_name" class="form-input" :disabled="!editing" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" v-model="profile.email" class="form-input" :disabled="!editing" />
                    </div>

                    <div class="form-group">
                        <label>Member Since</label>
                        <input type="text" :value="formatDate(profile.date_joined)" disabled
                            class="form-input disabled" />
                    </div>

                    <div class="form-actions">
                        <button v-if="!editing" type="button" @click="editing = true" class="btn btn-primary">
                            <i class="fas fa-edit"></i> Edit Profile
                        </button>

                        <template v-else>
                            <button type="submit" class="btn btn-success" :disabled="saving">
                                <i class="fas" :class="saving ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                                {{ saving ? 'Saving...' : 'Save Changes' }}
                            </button>
                            <button type="button" @click="cancelEdit" class="btn btn-secondary" :disabled="saving">
                                <i class="fas fa-times"></i> Cancel
                            </button>
                        </template>
                    </div>

                    <div v-if="successMessage" class="success-message">
                        <i class="fas fa-check-circle"></i> {{ successMessage }}
                    </div>
                    <div v-if="errorMessage" class="error-message">
                        <i class="fas fa-exclamation-circle"></i> {{ errorMessage }}
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const profile = ref({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    date_joined: ''
})

const originalProfile = ref({})
const editing = ref(false)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const loadProfile = async () => {
    try {
        const data = await api.getUserProfile()
        profile.value = data
        originalProfile.value = { ...data }
    } catch (error) {
        console.error('Failed to load profile:', error)
        errorMessage.value = 'Failed to load profile'
    }
}

const saveProfile = async () => {
    saving.value = true
    successMessage.value = ''
    errorMessage.value = ''

    try {
        const data = await api.updateUserProfile({
            first_name: profile.value.first_name,
            last_name: profile.value.last_name,
            email: profile.value.email,
        })

        profile.value = data
        originalProfile.value = { ...data }
        editing.value = false
        successMessage.value = 'Profile updated successfully!'

        setTimeout(() => {
            successMessage.value = ''
        }, 3000)
    } catch (error: any) {
        console.error('Failed to save profile:', error)
        errorMessage.value = error.response?.data?.error || 'Failed to save profile'
    } finally {
        saving.value = false
    }
}

const cancelEdit = () => {
    profile.value = { ...originalProfile.value }
    editing.value = false
    errorMessage.value = ''
}

const formatDate = (date: string) => {
    if (!date) return ''
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

onMounted(() => {
    loadProfile()
})
</script>

<style scoped>
.profile-page {
    min-height: 100vh;
    background: #f5f5f5;
    padding: 2rem;
}

.profile-container {
    max-width: 600px;
    margin: 0 auto;
}

.profile-header {
    margin-bottom: 2rem;
}

.profile-header h1 {
    font-size: 2rem;
    color: #1f2937;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.profile-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

label {
    display: block;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.form-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 1rem;
    transition: all 0.2s;
}

.form-input:focus {
    outline: none;
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input.disabled {
    background: #f9fafb;
    color: #9ca3af;
    cursor: not-allowed;
}

small {
    display: block;
    margin-top: 0.25rem;
    color: #6b7280;
    font-size: 0.75rem;
}

.form-actions {
    display: flex;
    gap: 0.75rem;
    margin-top: 2rem;
}

.btn {
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    border: none;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-primary {
    background: #6366f1;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: #4f46e5;
}

.btn-success {
    background: #10b981;
    color: white;
}

.btn-success:hover:not(:disabled) {
    background: #059669;
}

.btn-secondary {
    background: #6b7280;
    color: white;
}

.btn-secondary:hover:not(:disabled) {
    background: #4b5563;
}

.success-message {
    margin-top: 1rem;
    padding: 0.75rem;
    background: #d1fae5;
    color: #065f46;
    border-radius: 6px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
}

.error-message {
    margin-top: 1rem;
    padding: 0.75rem;
    background: #fee2e2;
    color: #991b1b;
    border-radius: 6px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
}
</style>
