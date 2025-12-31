import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NotebookList from './NotebookList.vue'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: {
    getNotebooks: vi.fn(),
    getPublicNotebooks: vi.fn(),
    deleteNotebook: vi.fn(),
  },
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/notebook/:id', component: { template: 'div' } }],
})

describe('NotebookList.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches and displays public notebooks when unauthenticated', async () => {
    const authStore = useAuthStore()
    authStore.token = null

    const mockPublicData = [
      {
        id: 1,
        title: 'Public R Analysis',
        author: 'UserA',
        is_public: true,
        updated_at: '2025-01-01',
      },
    ]
    vi.mocked(api.getPublicNotebooks).mockResolvedValue(mockPublicData)

    const wrapper = mount(NotebookList, { global: { plugins: [router] } })

    await flushPromises()

    expect(api.getPublicNotebooks).toHaveBeenCalled()
    expect(wrapper.find('h1').text()).toBe('Public Notebooks')
    expect(wrapper.findAll('.notebook-card')).toHaveLength(1)
    expect(wrapper.find('.notebook-card h3').text()).toBe('Public R Analysis')
  })

  it('fetches and displays user notebooks when authenticated', async () => {
    const authStore = useAuthStore()
    authStore.token = 'fake-token'

    const mockUserData = [
      {
        id: 2,
        title: 'My Private Study',
        author: 'Me',
        is_public: false,
        updated_at: '2025-12-31',
      },
    ]
    vi.mocked(api.getNotebooks).mockResolvedValue(mockUserData)

    const wrapper = mount(NotebookList, { global: { plugins: [router] } })

    await flushPromises()

    expect(api.getNotebooks).toHaveBeenCalled()
    expect(wrapper.find('h1').text()).toBe('My Notebooks')
    expect(wrapper.find('.private-badge').exists()).toBe(true)
  })

  it('navigates to the editor when a card is clicked', async () => {
    const authStore = useAuthStore()
    authStore.token = 'fake-token'
    vi.mocked(api.getNotebooks).mockResolvedValue([{ id: 99, title: 'Test' }])
    const pushSpy = vi.spyOn(router, 'push')

    const wrapper = mount(NotebookList, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.find('.notebook-card').trigger('click')
    expect(pushSpy).toHaveBeenCalledWith('/notebook/99')
  })

  it('deletes a notebook and updates the list', async () => {
    vi.stubGlobal(
      'confirm',
      vi.fn(() => true),
    )

    const authStore = useAuthStore()
    authStore.token = 'fake-token'
    vi.mocked(api.getNotebooks).mockResolvedValue([{ id: 10, title: 'To Delete' }])
    vi.mocked(api.deleteNotebook).mockResolvedValue({ success: true })

    const wrapper = mount(NotebookList, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.find('.btn-danger').trigger('click')

    expect(api.deleteNotebook).toHaveBeenCalledWith(10)
    expect(wrapper.findAll('.notebook-card')).toHaveLength(0)
  })
})
