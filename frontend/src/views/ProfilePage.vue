<script setup lang="ts">
/**
 * ProfilePage Component.
 * * Manages the authenticated user's personal information. This component 
 * implements a "Buffered Edit" pattern:
 * 1. Fetches user data on mount and stores it in the 'profile' ref.
 * 2. Maintains an 'originalProfile' copy to allow users to discard changes 
 * via a "Cancel" operation without extra API calls.
 * 3. Enforces strict input rules (e.g., immutable username).
 */

import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { getErrorMessage } from '@/utils/helpers'

/** * Defines the structure of the user profile record.
 */
interface ProfileData {
    username: string
    email: string
    first_name: string
    last_name: string
    date_joined: string
}

/** @type {import('vue').Ref<ProfileData>} The current reactive state of the form fields */
const profile = ref<ProfileData>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    date_joined: '',
})

/** * @type {import('vue').Ref<ProfileData>} 
 * Backup of the data retrieved from the server, used to restore the form 
 * if the user cancels an edit session.
 */
const originalProfile = ref<ProfileData>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    date_joined: '',
})

/** UI state flags for controlling the form's interactivity and feedback */
const editing = ref(false)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

/**
 * Data Initialization.
 * Retrieves the profile from the API and initializes both the active 
 * state and the backup copy.
 * @returns {Promise<void>}
 */
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

/**
 * Persistence Handler.
 * Sends updated profile data to the server. On success, it synchronizes 
 * the local backup and resets the UI to read-only mode.
 * @returns {Promise<void>}
 */
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

        // Temporary UI feedback: clear success message after 3 seconds
        setTimeout(() => {
            successMessage.value = ''
        }, 3000)
    } catch (err: unknown) {
        console.error('Failed to save profile:', err)
        errorMessage.value = getErrorMessage(err)
    } finally {
        saving.value = false
    }
}

/**
 * State Reversion.
 * Restores the 'profile' state from the 'originalProfile' backup and exits edit mode.
 */
const cancelEdit = () => {
    profile.value = { ...originalProfile.value }
    editing.value = false
    errorMessage.value = ''
}

/**
 * Formatting Utility.
 * Converts ISO timestamps into a localized, user-friendly format (e.g., January 1, 2026).
 * @param {string} date - ISO date string
 * @returns {string}
 */
const formatDate = (date: string) => {
    if (!date) return ''
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    })
}

onMounted(() => {
    loadProfile()
})
</script>

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