import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

vi.mock('@/services/api')

describe('Auth Store', () => {
  let setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
  let removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem')

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    localStorage.clear()

    setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
    removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem')
  })

  describe('login', () => {
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
    it('clears token and user data', () => {
      const store = useAuthStore()
      store.token = 'test-token'
      store.user = { id: 1, username: 'test', email: 'test@test.com' }

      store.logout()

      expect(store.token).toBeNull()
      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('removes data from localStorage', () => {
      const store = useAuthStore()
      store.logout()

      expect(removeItemSpy).toHaveBeenCalledWith('token')
      expect(removeItemSpy).toHaveBeenCalledWith('user')
    })
  })

  describe('clearError', () => {
    it('clears error message', () => {
      const store = useAuthStore()
      store.error = 'Some error'

      store.clearError()

      expect(store.error).toBeNull()
    })
  })
})
