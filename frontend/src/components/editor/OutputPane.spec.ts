import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import OutputPane from './OutputPane.vue'
import { useNotebookStore } from '@/stores/notebookStore'

describe('OutputPane.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders empty state initially', () => {
    const wrapper = mount(OutputPane, {
      props: { result: null, error: null, isLoading: false },
    })
    expect(wrapper.find('.output-empty').exists()).toBe(true)
    expect(wrapper.text()).toContain('Click "Run" to execute')
  })

  it('renders loading spinner when isLoading is true', () => {
    const wrapper = mount(OutputPane, {
      props: { result: null, error: null, isLoading: true },
    })
    expect(wrapper.find('.status-running').exists()).toBe(true)
    expect(wrapper.find('.fa-spinner').exists()).toBe(true)
  })

  it('renders iframe when result is provided', () => {
    const mockHtml = '<html><body>R Output</body></html>'
    const wrapper = mount(OutputPane, {
      props: { result: mockHtml, error: null, isLoading: false },
    })
    const iframe = wrapper.find('iframe')
    expect(iframe.exists()).toBe(true)
    expect(iframe.attributes('srcdoc')).toBe(mockHtml)
    expect(wrapper.find('.status-success').exists()).toBe(true)
  })

  it('parses and displays R execution errors correctly', () => {
    const rawError = 'Error in 1 + "a" : non-numeric argument to binary operator\nExecution halted'
    const wrapper = mount(OutputPane, {
      props: { result: null, error: rawError, isLoading: false },
    })

    expect(wrapper.find('.output-error').exists()).toBe(true)
    expect(wrapper.find('.highlighted-error pre').text()).toContain('Error in 1 + "a"')
    expect(wrapper.find('.error-details').text()).toBe(rawError)
  })

  it('prioritizes save errors from the store over execution errors', async () => {
    const store = useNotebookStore()
    store.saveError = 'Validation failed: title too short'

    const wrapper = mount(OutputPane, {
      props: {
        result: null,
        error: 'Some execution error',
        isLoading: false,
      },
    })

    expect(wrapper.find('.output-save-error').exists()).toBe(true)
    expect(wrapper.find('.highlighted-error pre').text()).toBe('Validation failed: title too short')
    expect(wrapper.find('.status-error').text()).toContain('Save Error')
  })

  it('calls store.clearErrors when retry button is clicked', async () => {
    const store = useNotebookStore()
    store.saveError = 'Error'
    const spy = vi.spyOn(store, 'clearErrors')

    const wrapper = mount(OutputPane, {
      props: { result: null, error: null, isLoading: false },
    })

    await wrapper.find('.btn-outline').trigger('click')
    expect(spy).toHaveBeenCalled()
  })
})
