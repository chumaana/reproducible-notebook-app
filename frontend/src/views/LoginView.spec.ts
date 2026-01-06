import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoginView from './LoginView.vue'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'

/** Mock router configuration for testing navigation behavior */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: { template: 'div' } },
    { path: '/notebooks', name: 'notebooks', component: { template: 'div' } },
  ],
})

/**
 * Test suite for LoginView.vue.
 * Verifies form rendering, input handling, error feedback, and the authentication workflow.
 */
describe('LoginView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  /**
   * Verifies the structural integrity of the login form.
   * Ensures essential elements (header, username input, password input) are present.
   */
  it('renders the login form correctly', () => {
    const wrapper = mount(LoginView, {
      global: { plugins: [router] },
    })

    expect(wrapper.find('h2').text()).toBe('Welcome Back')
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })

  /**
   * Tests two-way data binding.
   * Verifies that user input correctly updates the component's internal state.
   */
  it('updates ref values when user types in inputs', async () => {
    const wrapper = mount(LoginView, {
      global: { plugins: [router] },
    })

    const usernameInput = wrapper.find('input[name="username"]')
    const passwordInput = wrapper.find('input[type="password"]')

    await usernameInput.setValue('testuser')
    await passwordInput.setValue('password123')

    expect((usernameInput.element as HTMLInputElement).value).toBe('testuser')
    expect((passwordInput.element as HTMLInputElement).value).toBe('password123')
  })

  /**
   * Ensures authentication errors from the store are visible to the user.
   */
  it('displays error message from authStore', async () => {
    const authStore = useAuthStore()
    authStore.error = 'Invalid credentials'

    const wrapper = mount(LoginView, {
      global: { plugins: [router] },
    })

    expect(wrapper.find('.error-msg').text()).toContain('Invalid credentials')
  })

  /**
   * Checks UI feedback during network requests.
   * The submit button should be disabled and show a loading state to prevent double submission.
   */
  it('disables button and shows loading text when authStore is loading', () => {
    const authStore = useAuthStore()
    authStore.loading = true

    const wrapper = mount(LoginView, {
      global: { plugins: [router] },
    })

    const button = wrapper.find('button')
    expect(button.attributes()).toHaveProperty('disabled')
    expect(button.text()).toBe('Signing in...')
  })

  /**
   * Verifies the complete authentication workflow.
   * Ensures that submitting the form triggers the store's login action and redirects on success.
   */
  it('calls authStore.login and redirects on success', async () => {
    const authStore = useAuthStore()
    // Mock the login action to return true
    const loginSpy = vi.spyOn(authStore, 'login').mockResolvedValue(true)
    const routerPushSpy = vi.spyOn(router, 'push')

    const wrapper = mount(LoginView, {
      global: { plugins: [router] },
    })

    await wrapper.find('input[name="username"]').setValue('user')
    await wrapper.find('input[type="password"]').setValue('pass')
    await wrapper.find('form').trigger('submit.prevent')

    expect(loginSpy).toHaveBeenCalledWith({
      username: 'user',
      password: 'pass',
    })
    expect(routerPushSpy).toHaveBeenCalledWith('/notebooks')
  })
})
