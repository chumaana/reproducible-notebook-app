import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AnalysisDrawer from './AnalysisDrawer.vue'

describe('AnalysisDrawer.vue', () => {
  const mockR4RData = {
    r_packages: ['base', 'stats', 'dplyr', 'ggplot2', 'tidyr', 'readr'],
    system_libs: ['libcurl4-openssl-dev'],
    files_accessed: 12,
  }

  const mockIssues = [
    {
      title: 'Absolute Path Detected',
      details: 'Found /home/user/data.csv',
      severity: 'high' as const,
      fix: 'Use relative paths',
      code: 'read.csv("/home/user/data.csv")',
      lines: [{ line_number: 10, code: 'read.csv("/home/user/data.csv")' }],
    },
  ]

  it('renders package count correctly', () => {
    const wrapper = mount(AnalysisDrawer, {
      props: {
        issues: [],
        code: '',
        packageLoading: false,
        hasStaticAnalysis: true,
        r4rData: mockR4RData,
      },
    })

    expect(wrapper.find('.count').text()).toBe('6')
    expect(wrapper.findAll('.package-tag')).toHaveLength(5)
    expect(wrapper.find('.show-more-btn').exists()).toBe(true)
  })

  it('expands package list when header is clicked', async () => {
    const wrapper = mount(AnalysisDrawer, {
      props: {
        issues: [],
        code: '',
        packageLoading: false,
        hasStaticAnalysis: true,
        r4rData: mockR4RData,
      },
    })

    await wrapper.find('.card-header').trigger('click')

    expect(wrapper.findAll('.package-tag')).toHaveLength(6)
    expect(wrapper.find('.metric-card').classes()).toContain('expanded')
  })

  it('formats line numbers correctly', () => {
    const wrapper = mount(AnalysisDrawer, {
      props: {
        issues: mockIssues,
        code: 'some code',
        packageLoading: false,
        hasStaticAnalysis: true,
      },
    })

    expect(wrapper.find('.issue-count').text()).toContain('Line(s): 5')
  })

  it('disables download button and shows spinner when packageLoading is true', () => {
    const wrapper = mount(AnalysisDrawer, {
      props: {
        issues: [],
        code: '',
        packageLoading: true,
        hasStaticAnalysis: true,
      },
    })

    const downloadBtn = wrapper.find('.btn-primary')
    expect(downloadBtn.attributes()).toHaveProperty('disabled')
    expect(downloadBtn.find('.fa-spinner').exists()).toBe(true)
    expect(downloadBtn.text()).toBe('Downloading...')
  })

  it('emits download event when primary button is clicked', async () => {
    const wrapper = mount(AnalysisDrawer, {
      props: {
        issues: [],
        code: '',
        packageLoading: false,
        hasStaticAnalysis: true,
      },
    })

    await wrapper.find('.btn-primary').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('download')
  })
})
