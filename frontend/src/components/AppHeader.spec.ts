import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AppHeader from './AppHeader.vue'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'

/** Mock router instance required to render RouterLink components without errors */
const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: { template: 'div' } }],
})

/**
 * Test suite for AppHeader.vue.
 * Verifies dynamic navigation rendering based on authentication state
 * and user session management (profile display, logout).
 */
describe('AppHeader.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  /**
   * Verifies that the navigation bar correctly adapts to an authenticated state,
   * displaying the user's profile information instead of login buttons.
   */
  it('renders user profile and logout when authenticated', async () => {
    const authStore = useAuthStore()

    // Simulate active session
    authStore.token = 'fake-valid-token'
    authStore.user = {
      id: 1,
      username: 'RUser123',
      email: 'test@example.com',
    }

    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router],
        stubs: { RouterLink: false },
      },
    })

    await flushPromises()

    const userLink = wrapper.find('.user-link')
    expect(userLink.exists()).toBe(true)
    expect(userLink.text()).toContain('RUser123')
  })

  /**
   * Tests the logout workflow: ensures the store action is dispatched
   * and the application correctly redirects the user to the login page.
   */
  it('calls logout and redirects on logout button click', async () => {
    const authStore = useAuthStore()
    authStore.token = 'fake-valid-token'
    authStore.user = { id: 1, username: 'RUser123', email: 'test@example.com' }

    // Spy on critical side effects: store action and router navigation
    const logoutSpy = vi.spyOn(authStore, 'logout').mockResolvedValue(undefined)
    const pushSpy = vi.spyOn(router, 'push')

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })

    await flushPromises()

    const logoutBtn = wrapper.find('.btn-logout')
    await logoutBtn.trigger('click')

    expect(logoutSpy).toHaveBeenCalled()
    expect(pushSpy).toHaveBeenCalledWith('/login')
  })
})
