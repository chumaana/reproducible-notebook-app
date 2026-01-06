import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import NotFoundView from './NotFoundView.vue'

/** * Mock router instance to test the "Back to Home" navigation logic.
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: { template: 'div' } }],
})

/**
 * Test suite for NotFoundView.vue.
 * Verifies the display of 404 error information and the availability of recovery navigation.
 */
describe('NotFoundView.vue', () => {
  /**
   * Checks if the component renders the standard 404 branding and error message.
   */
  it('renders the 404 error message', () => {
    const wrapper = mount(NotFoundView, {
      global: { plugins: [router] },
    })

    expect(wrapper.find('h1').text()).toBe('404')
    expect(wrapper.text()).toContain('Page not found')
  })

  /**
   * Verifies the presence of a "Home" link.
   * This is critical for UX to ensure users are not stuck on a dead-end page.
   */
  it('contains a functional link back to home', () => {
    const wrapper = mount(NotFoundView, {
      global: { plugins: [router] },
    })

    const homeLink = wrapper.findComponent({ name: 'RouterLink' })
    expect(homeLink.exists()).toBe(true)
    expect(homeLink.props('to')).toBe('/')
  })
})
