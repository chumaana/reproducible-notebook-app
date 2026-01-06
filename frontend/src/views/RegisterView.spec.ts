import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RegisterView from './RegisterView.vue'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'

/** Mock router setup to validate post-registration navigation paths */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/register', component: { template: 'div' } },
    { path: '/notebooks', component: { template: 'div' } },
    { path: '/login', component: { template: 'div' } },
  ],
})

/**
 * Test suite for RegisterView.vue.
 * Verifies the user registration workflow, including form data handling,
 * store interaction, and automatic redirection upon success.
 */
describe('RegisterView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  /**
   * Tests the complete registration lifecycle.
   * Ensures that providing valid credentials triggers the auth store action
   * and subsequently moves the user to their private dashboard.
   */
  it('calls register and redirects to notebooks on success', async () => {
    const authStore = useAuthStore()

    // Spy on authentication actions to verify they are called with correct data
    const registerSpy = vi.spyOn(authStore, 'register').mockResolvedValue(true)
    const loginSpy = vi.spyOn(authStore, 'login').mockResolvedValue(true)
    const pushSpy = vi.spyOn(router, 'push')

    // Simulate an issued token to reflect an authenticated session state
    authStore.token = 'fake-token'

    const wrapper = mount(RegisterView, {
      global: { plugins: [router] },
    })

    // Simulate user filling out the registration form
    await wrapper.find('input[name="username"]').setValue('validuser')
    await wrapper.find('input[type="email"]').setValue('valid@test.com')
    await wrapper.find('input[name="password"]').setValue('secret123')
    await wrapper.find('input[name="rePassword"]').setValue('secret123')

    // Trigger form submission
    await wrapper.find('form').trigger('submit.prevent')

    // Wait for all asynchronous store and router actions to resolve
    await flushPromises()

    expect(registerSpy).toHaveBeenCalled()
    expect(pushSpy).toHaveBeenCalledWith('/notebooks')
  })
})
