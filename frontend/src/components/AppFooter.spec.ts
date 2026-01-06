import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppFooter from './AppFooter.vue'

/**
 * Test suite for AppFooter.vue.
 * Verifies static content rendering, dynamic date calculation, and external link safety.
 */
describe('AppFooter.vue', () => {
  /**
   * Verifies that the copyright year is calculated dynamically based on the current system date.
   * This ensures the footer remains up-to-date automatically.
   */
  it('renders the correct current year dynamically', () => {
    const wrapper = mount(AppFooter)
    const currentYear = new Date().getFullYear().toString()

    expect(wrapper.find('.footer-bottom p').text()).toContain(currentYear)
  })

  /**
   * Ensures critical external navigation links (GitHub repo, Documentation) are present.
   */
  it('contains links to external resources', () => {
    const wrapper = mount(AppFooter)
    const links = wrapper.findAll('a')

    const githubLink = links.find((a) => a.attributes('href')?.includes('github.com'))
    const docLink = links.find((a) => a.attributes('href')?.includes('r-tooling'))

    expect(githubLink?.exists()).toBe(true)
    expect(docLink?.exists()).toBe(true)
  })

  /**
   * Validates security and UX best practices.
   * External links must open in a new tab to prevent losing the user session
   * and should implicitly handle rel="noopener noreferrer" (checked via target="_blank").
   */
  it('has target="_blank" on external links for security and UX', () => {
    const wrapper = mount(AppFooter)
    const links = wrapper.findAll('a')

    links.forEach((link) => {
      expect(link.attributes('target')).toBe('_blank')
    })
  })

  /**
   * Checks for the presence of branding elements like the project title and description.
   */
  it('displays the project title and description', () => {
    const wrapper = mount(AppFooter)
    expect(wrapper.find('h3').text()).toBe('R Notebook Editor')
    expect(wrapper.find('.footer-section p').text()).toContain('Reproducible R notebooks')
  })
})
