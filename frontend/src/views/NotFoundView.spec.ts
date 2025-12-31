import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import NotFoundView from './NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: { template: 'div' } }],
})

describe('NotFoundView.vue', () => {
  it('renders the 404 error message', () => {
    const wrapper = mount(NotFoundView, {
      global: { plugins: [router] },
    })

    expect(wrapper.find('h1').text()).toBe('404')
    expect(wrapper.text()).toContain('Page not found')
  })

  it('contains a functional link back to home', () => {
    const wrapper = mount(NotFoundView, {
      global: { plugins: [router] },
    })

    const homeLink = wrapper.findComponent({ name: 'RouterLink' })
    expect(homeLink.exists()).toBe(true)
    expect(homeLink.props('to')).toBe('/')
  })
})
