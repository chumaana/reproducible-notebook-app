import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelpView from './HelpView.vue'

describe('HelpView.vue', () => {
  it('renders all main help sections', () => {
    const wrapper = mount(HelpView)

    expect(wrapper.find('#getting-started').exists()).toBe(true)
    expect(wrapper.find('#editor').exists()).toBe(true)
    expect(wrapper.find('#reproducibility').exists()).toBe(true)
  })

  it('displays the reproducibility workflow steps in order', () => {
    const wrapper = mount(HelpView)
    const steps = wrapper.findAll('.workflow-step-help')

    expect(steps).toHaveLength(4)
    expect(steps[0].text()).toContain('Run')
    expect(steps[1].text()).toContain('Package')
    expect(steps[2].text()).toContain('Diff')
    expect(steps[3].text()).toContain('Download')
  })

  it('contains the R Markdown code example', () => {
    const wrapper = mount(HelpView)
    const codeBlock = wrapper.find('pre code')

    expect(codeBlock.exists()).toBe(true)
    expect(codeBlock.text()).toContain('title: "Your Notebook Title"')
    expect(codeBlock.text()).toContain('```{r}')
  })

  it('renders quick links with correct href anchors', () => {
    const wrapper = mount(HelpView)
    const quickLinks = wrapper.findAll('.quick-link')

    expect(quickLinks[0].attributes('href')).toBe('#getting-started')
    expect(quickLinks[1].attributes('href')).toBe('#editor')
    expect(quickLinks[2].attributes('href')).toBe('#reproducibility')
  })
})
