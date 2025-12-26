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
                <RouterLink to="/notebook/new" class="btn btn-primary">
                    <i class="fas fa-plus"></i>
                    Create Notebook
                </RouterLink>
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

<style scoped>
.notebooks-page {
    min-height: calc(100vh - 70px);
    padding: var(--space-8) 0;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-8);
}

.page-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-gray-800);
    margin-bottom: var(--space-1);
}

.page-description {
    color: var(--color-gray-600);
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-12);
    color: var(--color-gray-500);
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--color-gray-200);
    border-left-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--space-4);
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.empty-state {
    text-align: center;
    padding: var(--space-12);
    color: var(--color-gray-500);
}

.empty-state i {
    font-size: 4rem;
    margin-bottom: var(--space-4);
    color: var(--color-gray-300);
}

.empty-state h2 {
    font-size: 1.5rem;
    color: var(--color-gray-700);
    margin-bottom: var(--space-2);
}

.empty-state p {
    margin-bottom: var(--space-6);
}

.notebooks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: var(--space-6);
}

.notebook-card {
    background: white;
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    cursor: pointer;
    transition: all 0.2s;
}

.notebook-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.notebook-card-header {
    padding: var(--space-5);
    border-bottom: 1px solid var(--color-gray-200);
    display: flex;
    justify-content: space-between;
    align-items: start;
}

.notebook-card-header h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-gray-800);
    margin: 0;
    flex: 1;
}

.notebook-actions {
    display: flex;
    gap: var(--space-2);
}

.notebook-card-body {
    padding: var(--space-5);
}

.notebook-meta {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    margin-bottom: var(--space-4);
}

.meta-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    color: var(--color-gray-600);
}

.notebook-stats {
    display: flex;
    gap: var(--space-4);
    padding-top: var(--space-3);
    border-top: 1px solid var(--color-gray-200);
}

.stat-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    color: var(--color-gray-700);
    font-weight: 500;
}

@media (max-width: 768px) {
    .page-header {
        flex-direction: column;
        align-items: stretch;
        gap: var(--space-4);
    }

    .notebooks-grid {
        grid-template-columns: 1fr;
    }
}
</style>
