import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Minimal router for the smoke test
const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
})

describe('App.vue Bootstrap', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders the application layout (Header and Footer)', async () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    })

    // Check for the presence of major layout components
    // (Assuming your App.vue uses these class names or components)
    expect(wrapper.findComponent({ name: 'AppHeader' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'AppFooter' }).exists()).toBe(true)
  })
})
