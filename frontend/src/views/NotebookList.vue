<template>
    <div class="notebooks-page">
        <div class="container">
            <div class="page-header">
                <div>
                    <h1>My Notebooks</h1>
                    <p class="page-description">Manage and organize your R notebooks</p>
                </div>
                <RouterLink to="/notebook/new" class="btn btn-primary">
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
                <h2>No notebooks yet</h2>
                <p>Create your first notebook to get started</p>
            </div>
            <div v-else class="notebooks-grid">
                <div v-for="notebook in notebooks" :key="notebook.id" class="notebook-card"
                    @click="openNotebook(notebook.id!)">
                    <div class="notebook-card-header">
                        <h3>{{ notebook.title }}</h3>
                        <div class="notebook-actions">
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
                        <div class="notebook-stats">
                            <span class="stat-item">
                                <!-- You can add stats here if needed -->
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
 * Notebook list view displaying all user notebooks.
 * Provides grid layout with create, open, and delete operations.
 */

import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import api from '@/services/api'
import type { Notebook } from '@/types/index'

const router = useRouter()
const notebooks = ref<Notebook[]>([])
const loading = ref(false)

/**
 * Loads all notebooks for the current user.
 */
const loadNotebooks = async () => {
    loading.value = true
    try {
        console.log('🔍 Fetching notebooks...')
        const data = await api.getNotebooks()
        notebooks.value = data
    } catch (error) {
        console.error('❌ Error loading notebooks:', error)
    } finally {
        loading.value = false
    }
}

/**
 * Navigates to the notebook editor page.
 * 
 * @param id - Notebook ID to open
 */
const openNotebook = (id: number) => {
    router.push(`/notebook/${id}`)
}

/**
 * Deletes a notebook after confirmation.
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