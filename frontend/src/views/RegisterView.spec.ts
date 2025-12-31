import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RegisterView from './RegisterView.vue'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/register', component: { template: 'div' } },
    { path: '/notebooks', component: { template: 'div' } },
    { path: '/login', component: { template: 'div' } },
  ],
})

describe('RegisterView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('calls register and redirects to notebooks on success', async () => {
    const authStore = useAuthStore()

    const registerSpy = vi.spyOn(authStore, 'register').mockResolvedValue(true)
    const loginSpy = vi.spyOn(authStore, 'login').mockResolvedValue(true)
    const pushSpy = vi.spyOn(router, 'push')

    authStore.token = 'fake-token'

    const wrapper = mount(RegisterView, {
      global: { plugins: [router] },
    })

    await wrapper.find('input[name="username"]').setValue('validuser')
    await wrapper.find('input[type="email"]').setValue('valid@test.com')
    await wrapper.find('input[name="password"]').setValue('secret123')
    await wrapper.find('input[name="rePassword"]').setValue('secret123')

    await wrapper.find('form').trigger('submit.prevent')

    await flushPromises()

    expect(registerSpy).toHaveBeenCalled()
    expect(pushSpy).toHaveBeenCalledWith('/notebooks')
  })
})
