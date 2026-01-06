import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

/** * Minimal router configuration to allow the root App component
 * to render its <router-view> during testing.
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
})

/**
 * Bootstrap test suite for the main App component.
 * Verifies that the global layout shell (Header, Footer, and Router view)
 * is correctly initialized and rendered.
 */
describe('App.vue Bootstrap', () => {
  beforeEach(() => {
    // Re-initialize the global state before each test
    setActivePinia(createPinia())
  })

  /**
   * Structural integrity test.
   * Ensures that the fundamental layout components are present,
   * confirming that the application shell is correctly composed.
   */
  it('renders the application layout (Header and Footer)', async () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    })

    // Check for the presence of major layout components
    // to ensure the consistent look-and-feel across all pages.
    expect(wrapper.findComponent({ name: 'AppHeader' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'AppFooter' }).exists()).toBe(true)
  })
})
