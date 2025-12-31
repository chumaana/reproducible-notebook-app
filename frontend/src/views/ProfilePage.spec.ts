import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ProfilePage from './ProfilePage.vue'
import api from '@/services/api'

/**
 * Mocking the API service to isolate the component logic from network calls.
 */
vi.mock('@/services/api', () => ({
  default: {
    getUserProfile: vi.fn(),
    updateUserProfile: vi.fn(),
  },
}))

describe('ProfilePage.vue', () => {
  const mockUser = {
    username: 'r_developer',
    email: 'dev@r-notebook.com',
    first_name: 'R',
    last_name: 'Coder',
    date_joined: '2025-01-01T10:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(api.getUserProfile).mockResolvedValue(mockUser)
  })

  it('loads and displays user profile data on mount', async () => {
    const wrapper = mount(ProfilePage)

    await flushPromises()

    expect(api.getUserProfile).toHaveBeenCalled()

    const usernameInput = wrapper.find('input[type="text"]')
    expect(usernameInput.attributes()).toHaveProperty('disabled')
    expect((usernameInput.element as HTMLInputElement).value).toBe('r_developer')

    const emailInput = wrapper.find('input[type="email"]')
    expect((emailInput.element as HTMLInputElement).value).toBe('dev@r-notebook.com')
  })

  it('toggles edit mode and unlocks inputs', async () => {
    const wrapper = mount(ProfilePage)
    await flushPromises()

    const firstNameInput = wrapper.findAll('input')[1]
    expect(firstNameInput.attributes()).toHaveProperty('disabled')

    await wrapper.find('.btn-primary').trigger('click')

    expect(firstNameInput.attributes()).not.toHaveProperty('disabled')
    expect(wrapper.find('.btn-success').text()).toContain('Save Changes')
  })

  it('restores original data when "Cancel" is clicked', async () => {
    const wrapper = mount(ProfilePage)
    await flushPromises()

    await wrapper.find('.btn-primary').trigger('click')
    const emailInput = wrapper.find('input[type="email"]')

    await emailInput.setValue('changed-email@test.com')
    expect((emailInput.element as HTMLInputElement).value).toBe('changed-email@test.com')

    await wrapper.find('.btn-secondary').trigger('click')

    expect((emailInput.element as HTMLInputElement).value).toBe('dev@r-notebook.com')
    expect(wrapper.find('.btn-primary').text()).toContain('Edit Profile')
  })

  it('shows success message and updates state on successful save', async () => {
    vi.mocked(api.updateUserProfile).mockResolvedValue({
      ...mockUser,
      first_name: 'Updated',
    })

    const wrapper = mount(ProfilePage)
    await flushPromises()

    await wrapper.find('.btn-primary').trigger('click')

    const inputs = wrapper.findAll('input')
    const firstNameInput = inputs[1]
    await firstNameInput.setValue('Updated')

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.find('.success-message').exists()).toBe(true)
    expect(wrapper.find('.success-message').text()).toContain('successfully')

    expect(wrapper.find('.btn-primary').exists()).toBe(true)
    expect(firstNameInput.attributes()).toHaveProperty('disabled')
  })
})
