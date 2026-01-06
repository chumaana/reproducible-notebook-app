import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CodeHighlighter from './CodeHighlighter.vue'

/**
 * Test suite for the CodeHighlighter component.
 * Verifies rendering logic, offset mapping for errors, and tooltip interactivity.
 */
describe('CodeHighlighter.vue', () => {
  /** @type {string} Sample R source code for testing */
  const mockCode = 'line1\nline2\nline3\nline4\nline5\nline6'

  /** * @type {Array} Mock analysis issues.
   * Note: 'line_number: 7' is used to test the YAML header offset calculation.
   */
  const mockIssues = [
    {
      title: 'Missing Library',
      severity: 'high',
      fix: 'Add library(dplyr)',
      lines: [{ line_number: 7, code: 'line2' }],
    },
  ]

  /**
   * Ensure the component correctly splits the input string into DOM elements.
   */
  it('renders the correct number of lines', () => {
    const wrapper = mount(CodeHighlighter, {
      props: { code: mockCode, issues: [] },
    })
    expect(wrapper.findAll('.code-line')).toHaveLength(6)
  })

  /**
   * Verify that issue classes are applied to the correct visual line.
   * Tests the mapping between backend line numbers (absolute) and frontend lines (relative).
   */
  it('applies error class using the RMARKDOWN_OFFSET', () => {
    const wrapper = mount(CodeHighlighter, {
      props: { code: mockCode, issues: mockIssues },
    })
    const line2 = wrapper.findAll('.code-line')[1]
    expect(line2.classes()).toContain('line-error')
    expect(line2.find('.issue-indicator').exists()).toBe(true)
  })

  /**
   * Test user interaction: tooltip should appear on hover and vanish on leave.
   */
  it('shows tooltip on mouseenter and hides on mouseleave', async () => {
    const wrapper = mount(CodeHighlighter, {
      props: { code: mockCode, issues: mockIssues },
    })
    const line2 = wrapper.findAll('.code-line')[1]

    await line2.trigger('mouseenter')
    const tooltip = wrapper.find('.issue-tooltip')
    expect(tooltip.exists()).toBe(true)
    expect(tooltip.text()).toContain('Missing Library')
    expect(tooltip.text()).toContain('Add library(dplyr)')

    await line2.trigger('mouseleave')
    expect(wrapper.find('.issue-tooltip').exists()).toBe(false)
  })

  /**
   * Edge case test: ensure the parser handles content without newline characters.
   */
  it('handles code with a single line', () => {
    const wrapper = mount(CodeHighlighter, {
      props: { code: 'single line', issues: [] },
    })
    expect(wrapper.findAll('.code-line')).toHaveLength(1)
  })
})
