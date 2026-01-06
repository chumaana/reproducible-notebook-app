import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

/**
 * Test suite for Vue Router navigation guards.
 * Verifies access control policies (Public vs Protected routes),
 * redirection logic for authentication states, and metadata management.
 */
describe('Router Navigation Guards', () => {
  beforeEach(async () => {
    // Reset state and router before each test to ensure isolation
    setActivePinia(createPinia())
    await router.push('/')
    await router.isReady()

    localStorage.clear()
  })

  /**
   * Verifies that public routes (e.g., Help, Community) are accessible
   * to anonymous users without redirection.
   */
  it('allows access to public routes for everyone', async () => {
    await router.push({ name: 'help' })
    expect(router.currentRoute.value.name).toBe('help')

    await router.push({ name: 'notebooks' })
    expect(router.currentRoute.value.name).toBe('notebooks')
  })

  /**
   * Security check: Ensures unauthenticated users attempting to access
   * protected routes (Profile) are redirected to the login page.
   * Also verifies that the intended destination is saved in query params.
   */
  it('redirects to login when accessing protected route while unauthenticated', async () => {
    const authStore = useAuthStore()
    authStore.token = null

    await router.push({ name: 'profile' })

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/profile')
  })

  /**
   * UX optimization: Prevents authenticated users from accessing 'guest-only'
   * pages (Login/Register) and redirects them to the dashboard/home.
   */
  it('redirects to home when authenticated user tries to access login/register', async () => {
    const authStore = useAuthStore()
    authStore.token = 'fake-valid-token'

    await router.push({ name: 'login' })
    expect(router.currentRoute.value.name).toBe('home')

    await router.push({ name: 'register' })
    expect(router.currentRoute.value.name).toBe('home')
  })

  /**
   * Usability check: Verifies that the global navigation guard correctly
   * updates the document title tag based on route metadata.
   */
  it('sets the document title based on route meta', async () => {
    await router.push({ name: 'help' })
    expect(document.title).toBe('Help - R Notebook Editor')
  })
})
