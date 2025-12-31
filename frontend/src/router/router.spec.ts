import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

describe('Router Navigation Guards', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    await router.push('/')
    await router.isReady()

    localStorage.clear()
  })

  it('allows access to public routes for everyone', async () => {
    await router.push({ name: 'help' })
    expect(router.currentRoute.value.name).toBe('help')

    await router.push({ name: 'notebooks' })
    expect(router.currentRoute.value.name).toBe('notebooks')
  })

  it('redirects to login when accessing protected route while unauthenticated', async () => {
    const authStore = useAuthStore()
    authStore.token = null

    await router.push({ name: 'profile' })

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/profile')
  })

  it('redirects to home when authenticated user tries to access login/register', async () => {
    const authStore = useAuthStore()
    authStore.token = 'fake-valid-token'

    await router.push({ name: 'login' })
    expect(router.currentRoute.value.name).toBe('home')

    await router.push({ name: 'register' })
    expect(router.currentRoute.value.name).toBe('home')
  })

  it('sets the document title based on route meta', async () => {
    await router.push({ name: 'help' })
    expect(document.title).toBe('Help - R Notebook Editor')
  })
})
