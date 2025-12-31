import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import EditorToolbar from './EditorToolbar.vue'

describe('EditorToolbar.vue', () => {
  const defaultProps = {
    isExecuting: false,
    isGenerating: false,
    isDiffing: false,
    isDownloading: false,
    hasExecuted: false,
    hasPackage: false,
    canDiff: false,
    canDownload: false,
  }

  it('emits save event when save button is clicked', async () => {
    const wrapper = mount(EditorToolbar, { props: defaultProps })
    await wrapper.find('#btn-save').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('save')
  })

  it('shows running state and disables button during execution', () => {
    const wrapper = mount(EditorToolbar, {
      props: { ...defaultProps, isExecuting: true },
    })
    const runBtn = wrapper.find('#btn-run')
    expect(runBtn.text()).toContain('Running...')
    expect(runBtn.find('.fa-spin').exists()).toBe(true)
    expect(runBtn.attributes()).toHaveProperty('disabled')
  })

  it('disables generate button until notebook has been executed', () => {
    const wrapper = mount(EditorToolbar, {
      props: { ...defaultProps, hasExecuted: false },
    })
    const generateBtn = wrapper.findAll('button').find((b) => b.text().includes('Generate Package'))
    expect(generateBtn?.attributes()).toHaveProperty('disabled')
    expect(generateBtn?.attributes('title')).toBe('Run notebook first')
  })

  it('renders refresh icon instead of text when package already exists', () => {
    const wrapper = mount(EditorToolbar, {
      props: { ...defaultProps, hasPackage: true, canDownload: true },
    })
    expect(wrapper.find('#btn-generate .fa-sync-alt').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('Generate Package')
  })

  it('disables modification actions but allows viewing actions in read-only mode', () => {
    const wrapper = mount(EditorToolbar, {
      props: {
        ...defaultProps,
        isReadOnly: true,
        hasPackage: true,
        canDownload: true,
      },
    })

    expect(wrapper.find('#btn-save').attributes()).toHaveProperty('disabled')
    expect(wrapper.find('#btn-run').attributes()).toHaveProperty('disabled')

    const analysisBtn = wrapper.findAll('button').find((b) => b.text().includes('Analysis'))
    const rmdBtn = wrapper.findAll('button').find((b) => b.text().includes('.Rmd'))

    expect(analysisBtn?.attributes()).not.toHaveProperty('disabled')
    expect(rmdBtn?.attributes()).not.toHaveProperty('disabled')
  })
})
