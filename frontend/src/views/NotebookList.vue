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

                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import api, { type Notebook } from '@/services/api'

const router = useRouter()
const notebooks = ref<Notebook[]>([])
const loading = ref(false)

const loadNotebooks = async () => {
    loading.value = true
    try {
        console.log('🔍 Fetching notebooks...')
        const data = await api.getNotebooks()
        notebooks.value = data
    } catch (error) {
        console.error(' Error loading notebooks:', error)
        console.error('Error details:', error.response?.data)
    } finally {
        loading.value = false
    }
}


const openNotebook = (id: number) => {
    router.push(`/notebook/${id}`)
}

const deleteNotebook = async (id: number) => {
    if (!confirm('Are you sure you want to delete this notebook?')) return

    try {
        await api.deleteNotebook(id)
        notebooks.value = notebooks.value.filter(n => n.id !== id)
    } catch (error) {
        console.error('Error deleting notebook:', error)
    }
}

const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    })
}

onMounted(() => {
    loadNotebooks()
})
</script>
