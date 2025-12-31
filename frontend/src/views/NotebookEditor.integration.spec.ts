import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NotebookEditor from '@/views/NotebookEditor.vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import api from '@/services/api'
import { useNotebookStore } from '../stores/notebookStore'

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

describe('NotebookEditor Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

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
