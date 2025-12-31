import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppFooter from './AppFooter.vue'

describe('AppFooter.vue', () => {
  it('renders the correct current year dynamically', () => {
    const wrapper = mount(AppFooter)
    const currentYear = new Date().getFullYear().toString()

    expect(wrapper.find('.footer-bottom p').text()).toContain(currentYear)
  })

  it('contains links to external resources', () => {
    const wrapper = mount(AppFooter)
    const links = wrapper.findAll('a')

    const githubLink = links.find((a) => a.attributes('href')?.includes('github.com'))
    const docLink = links.find((a) => a.attributes('href')?.includes('r-tooling'))

    expect(githubLink?.exists()).toBe(true)
    expect(docLink?.exists()).toBe(true)
  })

  it('has target="_blank" on external links for security and UX', () => {
    const wrapper = mount(AppFooter)
    const links = wrapper.findAll('a')

    links.forEach((link) => {
      expect(link.attributes('target')).toBe('_blank')
    })
  })

  it('displays the project title and description', () => {
    const wrapper = mount(AppFooter)
    expect(wrapper.find('h3').text()).toBe('R Notebook Editor')
    expect(wrapper.find('.footer-section p').text()).toContain('Reproducible R notebooks')
  })
})
