import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Import Font Awesome CSS - CRITICAL
import '@fortawesome/fontawesome-free/css/all.css'

// Import your routes/views
import Home from './views/HomeView.vue'
import NotebookList from './views/NotebookList.vue'
import NotebookEditor from './views/NotebookEditor.vue'

// Import global styles (if you have them)
import './assets/main.css'

const routes = [
  { path: '/', component: Home },
  { path: '/notebooks', component: NotebookList },
  { path: '/notebook/:id', component: NotebookEditor },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
app.use(router)
app.mount('#app')
