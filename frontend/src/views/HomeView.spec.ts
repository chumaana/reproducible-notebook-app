import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './HomeView.vue'

/**
 * Mock router setup for testing navigation links within the HomeView.
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: 'div' } },
    { path: '/notebook/new', component: { template: 'div' } },
    { path: '/notebooks', component: { template: 'div' } },
  ],
})

/**
 * Test suite for HomeView.vue.
 * Verifies the landing page structure, including hero section, call-to-actions (CTA),
 * feature highlights, and workflow visualization.
 */
describe('HomeView.vue', () => {
  /**
   * Tests the visibility of key branding elements.
   * Uses regex matching to account for potential HTML whitespace formatting in the title.
   */
  it('renders the hero title and main lead text', async () => {
    const wrapper = mount(HomeView, {
      global: { plugins: [router] },
    })

    // Fix: Use a regex to allow for the line break/whitespace difference
    expect(wrapper.find('h1').text()).toMatch(/R Notebooks That\s*Actually Reproduce/)
    expect(wrapper.find('.hero-lead').exists()).toBe(true)
  })

  /**
   * Verifies navigation paths.
   * Ensures the primary "New Notebook" and secondary "Browse" buttons
   * link to the correct application routes using the router mock.
   */
  it('contains correctly mapped CTA buttons', async () => {
    const wrapper = mount(HomeView, {
      global: { plugins: [router] },
    })

    const primaryCta = wrapper.find('.btn-hero-primary')
    const secondaryCta = wrapper.find('.btn-hero-secondary')

    // Fix: RouterLink renders as <a>, and 'to' becomes 'href'
    expect(primaryCta.attributes('href')).toBe('/notebook/new')
    expect(secondaryCta.attributes('href')).toBe('/notebooks')
  })

  /**
   * Checks for the presence of the product feature grid.
   * Ensures all 6 core features (Docker, Analysis, etc.) are rendered to the user.
   */
  it('renders all 6 feature cards', () => {
    const wrapper = mount(HomeView, {
      global: { plugins: [router] },
    })

    const featureCards = wrapper.findAll('.feature-card')
    expect(featureCards).toHaveLength(6)
    expect(wrapper.text()).toContain('Docker Export')
    expect(wrapper.text()).toContain('Static Analysis')
  })

  /**
   * Verifies the "How it works" section.
   * Ensures the logical progression of steps (Write -> ... -> Download) is displayed in the correct order.
   */
  it('displays the workflow steps in order', () => {
    const wrapper = mount(HomeView, {
      global: { plugins: [router] },
    })

    const steps = wrapper.findAll('.workflow-step')
    expect(steps).toHaveLength(5)
    expect(steps[0].text()).toContain('Write R Code')
    expect(steps[4].text()).toContain('Download & Share')
  })
})
