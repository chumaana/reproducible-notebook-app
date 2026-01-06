/**
 * Vue Router configuration for the R Notebook Editor application.
 * Defines routes, navigation guards, and scroll behavior.
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: {
      title: 'Home - R Notebook Editor',
      requiresAuth: false,
    },
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@/views/HelpView.vue'),
    meta: {
      title: 'Help - R Notebook Editor',
      requiresAuth: false,
    },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: 'Login',
      requiresAuth: false,
      guestOnly: true,
    },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: {
      title: 'Register',
      requiresAuth: false,
      guestOnly: true,
    },
  },
  {
    path: '/notebooks',
    name: 'notebooks',
    component: () => import('@/views/NotebookList.vue'),
    meta: {
      title: 'My Notebooks',
      requiresAuth: false,
    },
  },
  {
    path: '/notebook/:id',
    name: 'notebook-editor',
    component: () => import('@/views/NotebookEditor.vue'),
    meta: {
      title: 'Editor',
      requiresAuth: false,
    },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfilePage.vue'),
    meta: {
      title: 'Profile',
      requiresAuth: true,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: '404 - Page Not Found',
      requiresAuth: false,
    },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Restore scroll position on back/forward navigation
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  },
})

/**
 * Navigation guard for authentication and page titles.
 * Redirects unauthenticated users to login, and authenticated users away from guest-only pages.
 */
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  document.title = (to.meta.title as string) || 'R Notebook Editor'

  const requiresAuth = to.meta.requiresAuth as boolean
  const guestOnly = to.meta.guestOnly as boolean
  const isAuthenticated = authStore.isAuthenticated

  if (requiresAuth && !isAuthenticated) {
    // Redirect to login if authentication required
    next({
      name: 'login',
      query: { redirect: to.fullPath },
    })
  } else if (guestOnly && isAuthenticated) {
    // Redirect authenticated users away from login/register pages
    next({ name: 'home' })
  } else {
    next()
  }
})

router.onError((error) => {
  console.error('Router error:', error)
})

export default router
