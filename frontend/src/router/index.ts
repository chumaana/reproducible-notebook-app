import { createRouter, createWebHistory } from 'vue-router'
import NotebookList from '@/views/NotebookList.vue'
import NotebookEditor from '@/views/NotebookEditor.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: NotebookList,
    },
    {
      path: '/notebooks',
      name: 'notebooks',
      component: NotebookList,
    },
    {
      path: '/notebook/:id',
      name: 'notebook-editor',
      component: NotebookEditor,
    },
  ],
})

export default router
