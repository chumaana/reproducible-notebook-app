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

            <div v-if="isAuthenticated" class="filter-tabs">
                <button @click="filterType = 'all'" :class="['filter-tab', { active: filterType === 'all' }]">
                    <i class="fas fa-list"></i>
                    All ({{ notebooks.length }})
                </button>
                <button @click="filterType = 'public'" :class="['filter-tab', { active: filterType === 'public' }]">
                    <i class="fas fa-globe"></i>
                    Public ({{ publicCount }})
                </button>
                <button @click="filterType = 'private'" :class="['filter-tab', { active: filterType === 'private' }]">
                    <i class="fas fa-lock"></i>
                    Private ({{ privateCount }})
                </button>
            </div>

            <div v-if="loading" class="loading-state">
                <div class="spinner"></div>
                <p>Loading notebooks...</p>
            </div>
            <div v-else-if="filteredNotebooks.length === 0" class="empty-state">
                <i class="fas fa-folder-open"></i>
                <h2>{{ emptyStateTitle }}</h2>
                <p>{{ emptyStateMessage }}</p>
            </div>
            <div v-else class="notebooks-grid">
                <div v-for="notebook in filteredNotebooks" :key="notebook.id" class="notebook-card"
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
 * - Authenticated users: Shows their own notebooks with filter options
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
const filterType = ref<'all' | 'public' | 'private'>('all')

const isAuthenticated = computed(() => authStore.isAuthenticated)

/**
 * Filter notebooks based on selected filter type.
 * Only applies to authenticated users.
 */
const filteredNotebooks = computed(() => {
    if (!isAuthenticated.value) {
        return notebooks.value
    }

    switch (filterType.value) {
        case 'public':
            return notebooks.value.filter(n => n.is_public === true)
        case 'private':
            return notebooks.value.filter(n => n.is_public === false)
        default:
            return notebooks.value
    }
})

/**
 * Count of public notebooks.
 */
const publicCount = computed(() => {
    return notebooks.value.filter(n => n.is_public === true).length
})

/**
 * Count of private notebooks.
 */
const privateCount = computed(() => {
    return notebooks.value.filter(n => n.is_public === false).length
})

/**
 * Dynamic empty state title based on filter.
 */
const emptyStateTitle = computed(() => {
    if (!isAuthenticated.value) {
        return 'No public notebooks yet'
    }

    switch (filterType.value) {
        case 'public':
            return 'No public notebooks'
        case 'private':
            return 'No private notebooks'
        default:
            return 'No notebooks yet'
    }
})

/**
 * Dynamic empty state message based on filter.
 */
const emptyStateMessage = computed(() => {
    if (!isAuthenticated.value) {
        return 'Check back later for shared notebooks'
    }

    switch (filterType.value) {
        case 'public':
            return 'Make a notebook public to share it with others'
        case 'private':
            return 'All your notebooks are currently public'
        default:
            return 'Create your first notebook to get started'
    }
})

/**
 * Loads notebooks based on authentication status.
 * - Authenticated: Load user's notebooks
 * - Unauthenticated: Load all public notebooks
 */
const loadNotebooks = async () => {
    loading.value = true
    try {
        if (isAuthenticated.value) {
            console.log('🔍 Fetching user notebooks...')
            const data = await api.getNotebooks()
            notebooks.value = data
        } else {
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

<style scoped>
/* Filter Tabs */
.filter-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid var(--border-color);
}

.filter-tab {
    padding: 0.75rem 1.5rem;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: -2px;
}

.filter-tab:hover {
    color: var(--primary-color);
    background: var(--background-secondary);
}

.filter-tab.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

.filter-tab i {
    font-size: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
    .filter-tabs {
        overflow-x: auto;
    }

    .filter-tab {
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        white-space: nowrap;
    }
}
</style>
