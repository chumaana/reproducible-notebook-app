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
