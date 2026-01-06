import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NotebookList from './NotebookList.vue'
import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'
import api from '@/services/api'
import type { Notebook } from '@/types'

// Mock the API service to simulate backend responses
vi.mock('@/services/api', () => ({
  default: {
    getNotebooks: vi.fn(),
    getPublicNotebooks: vi.fn(),
    deleteNotebook: vi.fn(),
  },
}))

/** Mock router to test navigation between the list and the editor */
const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/notebook/:id', component: { template: 'div' } }],
})

/**
 * Test suite for the NotebookList component.
 * Verifies the dashboard behavior for different user states (Guest vs Authenticated),
 * navigation flow, and record management (deletion).
 */
describe('NotebookList.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  /**
   * Verifies that unauthenticated users can only view public resources.
   * Ensures the component correctly switches to the public API feed.
   */
  it('fetches and displays public notebooks when unauthenticated', async () => {
    const authStore = useAuthStore()
    authStore.token = null

    const mockPublicData: Notebook[] = [
      {
        id: 1,
        title: 'Public R Analysis',
        content: '',
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

  /**
   * Verifies that authenticated users see their private workspace.
   * Checks for UI indicators like the "Private" badge.
   */
  it('fetches and displays user notebooks when authenticated', async () => {
    const authStore = useAuthStore()
    authStore.token = 'fake-token'

    const mockUserData: Notebook[] = [
      {
        id: 2,
        title: 'My Private Study',
        content: '',
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

  /**
   * Tests the navigation trigger.
   * Clicking a notebook card should use the router to navigate to the editor.
   */
  it('navigates to the editor when a card is clicked', async () => {
    const authStore = useAuthStore()
    authStore.token = 'fake-token'

    const mockNotebook: Notebook = {
      id: 99,
      title: 'Test',
      content: '',
    }

    vi.mocked(api.getNotebooks).mockResolvedValue([mockNotebook])
    const pushSpy = vi.spyOn(router, 'push')

    const wrapper = mount(NotebookList, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.find('.notebook-card').trigger('click')
    expect(pushSpy).toHaveBeenCalledWith('/notebook/99')
  })

  /**
   * Tests the deletion workflow.
   * Verifies confirmation dialog handling, API interaction,
   * and reactive UI update (removing the item from the list).
   */
  it('deletes a notebook and updates the list', async () => {
    // Mock the native browser confirmation dialog
    vi.stubGlobal(
      'confirm',
      vi.fn(() => true),
    )

    const authStore = useAuthStore()
    authStore.token = 'fake-token'

    const mockNotebook: Notebook = {
      id: 10,
      title: 'To Delete',
      content: '',
    }

    vi.mocked(api.getNotebooks).mockResolvedValue([mockNotebook])
    vi.mocked(api.deleteNotebook).mockResolvedValue(undefined)

    const wrapper = mount(NotebookList, { global: { plugins: [router] } })
    await flushPromises()

    // Trigger deletion (ensure event modifiers like .stop are tested implicitly)
    await wrapper.find('.btn-danger').trigger('click')

    expect(api.deleteNotebook).toHaveBeenCalledWith(10)
    expect(wrapper.findAll('.notebook-card')).toHaveLength(0)
  })
})
