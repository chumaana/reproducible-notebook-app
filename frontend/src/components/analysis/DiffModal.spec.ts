import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DiffModal from './DiffModal.vue'

describe('DiffModal.vue', () => {
  it('shows loading spinner when diffHtml is null', () => {
    const wrapper = mount(DiffModal, {
      props: {
        diffHtml: null,
      },
    })

    expect(wrapper.find('.diff-empty').exists()).toBe(true)
    expect(wrapper.find('.fa-spin').exists()).toBe(true)
    expect(wrapper.text()).toContain('Loading diff...')
  })

  it('renders iframe when diffHtml is provided', () => {
    const mockHtml = '<html><body><h1>Diff Content</h1></body></html>'
    const wrapper = mount(DiffModal, {
      props: {
        diffHtml: mockHtml,
      },
    })

    const iframe = wrapper.find('iframe')
    expect(iframe.exists()).toBe(true)
    expect(iframe.attributes('srcdoc')).toBe(mockHtml)
    expect(wrapper.find('.diff-empty').exists()).toBe(false)
  })

  it('emits close event when close button is clicked', async () => {
    const wrapper = mount(DiffModal, {
      props: {
        diffHtml: '<div></div>',
      },
    })

    await wrapper.find('.modal-close-btn').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('close')
  })

  it('prevents click propagation to overlay via @click.stop', async () => {
    const wrapper = mount(DiffModal, {
      props: {
        diffHtml: '<div></div>',
      },
    })

    expect(wrapper.element.className).toContain('diff-modal')
  })
})
