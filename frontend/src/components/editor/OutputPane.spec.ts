import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import OutputPane from './OutputPane.vue'
import { useNotebookStore } from '@/stores/notebookStore'

/**
 * Test suite for OutputPane.vue.
 * Verifies the display logic for R execution results, loading states,
 * and the error handling hierarchy between execution and storage layers.
 */
describe('OutputPane.vue', () => {
  beforeEach(() => {
    // Reset Pinia state before each test to ensure isolation
    setActivePinia(createPinia())
  })

  /**
   * Verify the default UI state.
   * Ensures instructions are shown when no execution has occurred yet.
   */
  it('renders empty state initially', () => {
    const wrapper = mount(OutputPane, {
      props: { result: null, error: null, isLoading: false },
    })
    expect(wrapper.find('.output-empty').exists()).toBe(true)
    expect(wrapper.text()).toContain('Click "Run" to execute')
  })

  /**
   * Test asynchronous feedback.
   * Ensures the user receives visual indication (spinner) during code execution.
   */
  it('renders loading spinner when isLoading is true', () => {
    const wrapper = mount(OutputPane, {
      props: { result: null, error: null, isLoading: true },
    })
    expect(wrapper.find('.status-running').exists()).toBe(true)
    expect(wrapper.find('.fa-spinner').exists()).toBe(true)
  })

  /**
   * Verify output isolation / Sandboxing.
   * Checks that HTML results are rendered inside an <iframe> using 'srcdoc'.
   * This prevents R-generated CSS/JS from affecting the main application.
   */
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

  /**
   * Test error parsing logic.
   * Ensures raw R error strings are formatted and highlighted for readability.
   */
  it('parses and displays R execution errors correctly', () => {
    const rawError = 'Error in 1 + "a" : non-numeric argument to binary operator\nExecution halted'
    const wrapper = mount(OutputPane, {
      props: { result: null, error: rawError, isLoading: false },
    })

    expect(wrapper.find('.output-error').exists()).toBe(true)
    expect(wrapper.find('.highlighted-error pre').text()).toContain('Error in 1 + "a"')
    expect(wrapper.find('.error-details').text()).toBe(rawError)
  })

  /**
   * Verify Error Hierarchy.
   * Critical infrastructure errors (Save/Network) from the store must take precedence
   * over transient execution errors passed via props.
   */
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

  /**
   * Test interaction with global state.
   * Verifies that UI actions (Retry button) trigger correct Store methods.
   */
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
