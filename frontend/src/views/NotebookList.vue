<template>
    <div class="notebooks-page">
        <div class="container">
            <div class="page-header">
                <div>
                    <h1>
                        {{ isAuthenticated ? 'My Notebooks' : 'Public Notebooks' }}
                    </h1>
                    <p class="page-description">
                        {{ isAuthenticated ? 'Manage and organize your R notebooks' : 'Explore notebooks shared by the community' }}
                    </p>
                </div>
                <RouterLink v-if="isAuthenticated" to="/notebook/new" class="btn btn-primary">
                    <i class="fas fa-plus"></i>
                    New Notebook
                </RouterLink>
            </div>
            <div v-if="loading" class="loading-state">
                <div class="spinner"></div>
                <p>Loading notebooks...</p>
            </div>
            <div v-else-if="notebooks.length === 0" class="empty-state">
                <i class="fas fa-folder-open"></i>
                <h2>{{ isAuthenticated ? 'No notebooks yet' : 'No public notebooks yet' }}</h2>
                <p>{{ isAuthenticated ? 'Create your first notebook to get started' : 'Check back later for shared notebooks' }}</p>
            </div>
            <div v-else class="notebooks-grid">
                <div v-for="notebook in notebooks" :key="notebook.id" class="notebook-card"
                    @click="openNotebook(notebook.id!)">
                    <div class="notebook-card-header">
                        <div class="title-with-badge">
                            <h3>{{ notebook.title }}</h3>
                            <span v-if="notebook.is_public" class="public-badge" title="This notebook is public">
                                <i class="fas fa-globe"></i>
                            </span>
                            <span v-else-if="isAuthenticated" class="private-badge" title="This notebook is private">
                                <i class="fas fa-lock"></i>
                            </span>
                        </div>
                        <div v-if="isAuthenticated" class="notebook-actions">
                            <button @click.stop="deleteNotebook(notebook.id!)" class="btn-icon btn-danger">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="notebook-card-body">
                        <div class="notebook-meta">
                            <span class="meta-item">
                                <i class="fas fa-user"></i>
                                {{ notebook.author || 'Unknown' }}
                            </span>
                            <span class="meta-item">
                                <i class="fas fa-clock"></i>
                                {{ formatDate(notebook.updated_at) }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
/**
 * Notebook list view displaying user notebooks or public notebooks.
 * - Authenticated users: Shows their own notebooks with edit/delete
 * - Unauthenticated users: Shows all public notebooks (read-only)
 */

import { ref, onMounted, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import type { Notebook } from '@/types/index'

const router = useRouter()
const authStore = useAuthStore()
const notebooks = ref<Notebook[]>([])
const loading = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)

/**
 * Loads notebooks based on authentication status.
 * - Authenticated: Load user's notebooks
 * - Unauthenticated: Load all public notebooks
 */
const loadNotebooks = async () => {
    loading.value = true
    try {
        if (isAuthenticated.value) {
            // Load user's notebooks (private + public)
            console.log('🔍 Fetching user notebooks...')
            const data = await api.getNotebooks()
            notebooks.value = data
        } else {
            // Load all public notebooks
            console.log('🌐 Fetching public notebooks...')
            const data = await api.getPublicNotebooks()
            notebooks.value = data
        }
    } catch (error) {
        console.error('❌ Error loading notebooks:', error)
    } finally {
        loading.value = false
    }
}

/**
 * Navigates to the notebook editor/viewer.
 * - Authenticated users can edit their own notebooks
 * - Anyone can view public notebooks (read-only if not owner)
 * 
 * @param id - Notebook ID to open
 */
const openNotebook = (id: number) => {
    router.push(`/notebook/${id}`)
}
/**
 * Deletes a notebook after confirmation.
 * Only available to authenticated users.
 * 
 * @param id - Notebook ID to delete
 */
const deleteNotebook = async (id: number) => {
    if (!confirm('Are you sure you want to delete this notebook?')) return

    try {
        await api.deleteNotebook(id)
        notebooks.value = notebooks.value.filter((n) => n.id !== id)
    } catch (error) {
        console.error('Error deleting notebook:', error)
    }
}

/**
 * Formats a date string for display.
 * 
 * @param dateString - ISO date string
 * @returns Formatted date string
 */
const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    })
}

onMounted(() => {
    loadNotebooks()
})
</script>
