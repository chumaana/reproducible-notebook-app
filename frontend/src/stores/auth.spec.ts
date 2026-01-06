import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

// Mock the API service to isolate store testing from network requests
vi.mock('@/services/api')

/**
 * Test suite for the Authentication Store (Pinia).
 * Verifies state management for Login, Registration, and Session persistence.
 */
describe('Auth Store', () => {
  let setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
  let removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem')

  beforeEach(() => {
    // Reset Pinia and LocalStorage before each test to ensure isolation
    setActivePinia(createPinia())
    vi.clearAllMocks()

    localStorage.clear()

    // Re-initialize spies
    setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
    removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem')
  })

  describe('login', () => {
    /**
     * Test successful authentication flow.
     * The store should update its state with the returned token and user profile.
     */
    it('sets token and user on successful login', async () => {
      const mockResponse = {
        token: 'test-token-123',
        user: { id: 1, username: 'testuser', email: 'test@test.com' },
      }

      vi.mocked(api.login).mockResolvedValue(mockResponse)

      const store = useAuthStore()
      const result = await store.login({ username: 'testuser', password: 'pass123' })

      expect(result).toBe(true)
      expect(store.token).toBe('test-token-123')
      expect(store.user).toEqual(mockResponse.user)
      expect(store.isAuthenticated).toBe(true)
    })

    /**
     * Test persistence.
     * Critical for UX: authentication data must be saved to LocalStorage
     * to keep the user logged in across page reloads.
     */
    it('stores token in localStorage', async () => {
      const mockResponse = {
        token: 'test-token-123',
        user: { id: 1, username: 'testuser', email: 'test@test.com' },
      }

      vi.mocked(api.login).mockResolvedValue(mockResponse)

      const store = useAuthStore()
      await store.login({ username: 'testuser', password: 'pass123' })

      expect(setItemSpy).toHaveBeenCalledWith('token', 'test-token-123')
      expect(setItemSpy).toHaveBeenCalledWith('user', JSON.stringify(mockResponse.user))
    })

    /**
     * Test error handling during login.
     * The store should capture API errors to display feedback to the user.
     */
    it('returns false and sets error on login failure', async () => {
      const mockError = {
        response: { data: { error: 'Invalid credentials' } },
      }

      vi.mocked(api.login).mockRejectedValue(mockError)

      const store = useAuthStore()
      const result = await store.login({ username: 'wrong', password: 'wrong' })

      expect(result).toBe(false)
      expect(store.error).toBeTruthy()
      expect(store.token).toBeNull()
    })

    /**
     * Test UI state management (loading indicators).
     * `loading` should be true only while the async request is pending.
     */
    it('sets loading state during login', async () => {
      vi.mocked(api.login).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  token: 'token',
                  user: { id: 1, username: 'test', email: 'test@test.com' },
                }),
              100,
            ),
          ),
      )

      const store = useAuthStore()
      const loginPromise = store.login({ username: 'test', password: 'pass' })

      expect(store.loading).toBe(true)

      await loginPromise

      expect(store.loading).toBe(false)
    })
  })

  describe('register', () => {
    /**
     * Test registration flow.
     * Following successful registration, the user should be automatically logged in.
     */
    it('registers user and auto-logs in', async () => {
      const mockResponse = {
        token: 'new-token-456',
        user: { id: 2, username: 'newuser', email: 'new@test.com' },
      }

      vi.mocked(api.register).mockResolvedValue(mockResponse)

      const store = useAuthStore()
      const result = await store.register({
        username: 'newuser',
        email: 'new@test.com',
        password: 'pass123',
      })

      expect(result).toBe(true)
      expect(store.token).toBe('new-token-456')
      expect(store.isAuthenticated).toBe(true)
    })

    /**
     * Test validation error handling during registration (e.g., duplicate username).
     */
    it('handles registration errors', async () => {
      const mockError = {
        response: {
          data: {
            username: ['Username already exists'],
          },
        },
        message: 'Request failed',
      }

      vi.mocked(api.register).mockRejectedValue(mockError)

      const store = useAuthStore()
      const result = await store.register({
        username: 'existing',
        email: 'test@test.com',
        password: 'pass123',
      })

      expect(result).toBe(false)
      expect(store.error).toBeTruthy()
    })
  })

  describe('logout', () => {
    /**
     * Test session termination.
     * All sensitive data must be wiped from the state.
     */
    it('clears token and user data', () => {
      const store = useAuthStore()
      store.token = 'test-token'
      store.user = { id: 1, username: 'test', email: 'test@test.com' }

      store.logout()

      expect(store.token).toBeNull()
      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    /**
     * Test persistence cleanup.
     * Sensitive data must be removed from LocalStorage to prevent unauthorized access.
     */
    it('removes data from localStorage', () => {
      const store = useAuthStore()
      store.logout()

      expect(removeItemSpy).toHaveBeenCalledWith('token')
      expect(removeItemSpy).toHaveBeenCalledWith('user')
    })
  })

  describe('clearError', () => {
    /**
     * Test utility for resetting error messages (e.g., when user retries input).
     */
    it('clears error message', () => {
      const store = useAuthStore()
      store.error = 'Some error'

      store.clearError()

      expect(store.error).toBeNull()
    })
  })
})
