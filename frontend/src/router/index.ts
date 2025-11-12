import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NotebookEditor from '../views/NotebookEditor.vue'
import NotebookList from '../views/NotebookList.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/notebook/:id',
      name: 'notebook-editor',
      component: NotebookEditor,
    },
    {
      path: '/notebooks',
      name: 'notebooks',
      component: NotebookList,
    },
  ],
})

export default router
