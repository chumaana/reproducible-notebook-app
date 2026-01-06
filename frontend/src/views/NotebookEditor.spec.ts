import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NotebookEditor from '@/views/NotebookEditor.vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import api from '@/services/api'
import { useNotebookStore } from '../stores/notebookStore'

// Mock dependencies to isolate component testing
vi.mock('@/services/api')

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: '1' } }),
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
}))

vi.mock('@/router', () => ({
  default: {
    push: vi.fn(),
    replace: vi.fn(),
  },
}))

/**
 * Integration Test Suite for NotebookEditor.vue.
 * Tests the full lifecycle of the editor: data loading, permission checks, and auto-save triggers.
 */
describe('NotebookEditor Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  /**
   * Verify Data Initialization.
   * Ensures that the component correctly fetches notebook details from the API
   * and populates the UI (title input) upon mounting.
   */
  it('loads notebook on mount', async () => {
    const mockNotebook = {
      id: 1,
      title: 'Test Notebook',
      content: '---\ntitle: Test Notebook\n---\n# R Code\nprint("test")',
      author: 'testuser',
      is_public: false,
    }

    vi.mocked(api.getNotebook).mockResolvedValue(mockNotebook)
    vi.mocked(api.getExecutions).mockResolvedValue([])

    const wrapper = mount(NotebookEditor, {
      global: {
        stubs: {
          EditorToolbar: true,
          OutputPane: true,
          AnalysisDrawer: true,
          DiffModal: true,
        },
      },
    })

    await flushPromises()

    const titleInput = wrapper.find('[data-testid="notebook-title-input"]')
    expect((titleInput.element as HTMLInputElement).value).toBe('Test Notebook')
  })

  /**
   * Verify Access Control UI.
   * Checks that a "Read Only" banner is displayed when the current user
   * is different from the notebook author (public view mode).
   */
  it('displays read-only banner for public notebooks not owned by user', async () => {
    localStorage.setItem('user', JSON.stringify({ username: 'otheruser' }))

    const mockNotebook = {
      id: 1,
      title: 'Public Notebook',
      content: '# Code',
      author: 'owner',
      is_public: true,
    }

    vi.mocked(api.getNotebook).mockResolvedValue(mockNotebook)
    vi.mocked(api.getExecutions).mockResolvedValue([])

    const wrapper = mount(NotebookEditor, {
      global: {
        stubs: {
          EditorToolbar: true,
          OutputPane: true,
          AnalysisDrawer: true,
          DiffModal: true,
        },
      },
    })

    await flushPromises()

    expect(wrapper.find('.read-only-banner').exists()).toBe(true)
    expect(wrapper.find('.read-only-banner').text()).toContain('owner')
  })

  /**
   * Verify User Interaction (Auto-save).
   * Ensures that the save action is triggered immediately when the title input loses focus.
   */
  it('triggers save on title blur', async () => {
    const store = useNotebookStore()
    const saveSpy = vi.spyOn(store, 'save').mockResolvedValue(1)

    const wrapper = mount(NotebookEditor, {
      global: {
        stubs: {
          EditorToolbar: true,
          OutputPane: true,
          AnalysisDrawer: true,
          DiffModal: true,
        },
      },
    })

    const titleInput = wrapper.find('[data-testid="notebook-title-input"]')
    await titleInput.trigger('blur')

    expect(saveSpy).toHaveBeenCalled()
  })
})
