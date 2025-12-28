import { defineStore } from 'pinia'
import api from '@/services/api'
import axios from 'axios'

interface User {
  id: number
  username: string
  email: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') as string | null,
    user: JSON.parse(localStorage.getItem('user') || 'null') as User | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (state): boolean => !!state.token,
  },

  actions: {
    async login(credentials: Record<string, string>) {
      this.loading = true
      this.error = null
      try {
        const response = await api.login(credentials)

        this.token = response.token
        this.user = response.user

        // 1. Persist to storage
        localStorage.setItem('token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))

        api.setToken(response.token)

        return true
      } catch (err: unknown) {
        this.error = this.handleError(err)
        return false
      } finally {
        this.loading = false
      }
    },

    async register(credentials: Record<string, string>) {
      this.loading = true
      this.error = null
      try {
        const response = await api.register(credentials)

        // If your backend returns token on registration
        if (response.token) {
          this.token = response.token
          this.user = response.user
          localStorage.setItem('token', response.token)
          localStorage.setItem('user', JSON.stringify(response.user))
          api.setToken(response.token)
        }
        return true
      } catch (err: unknown) {
        this.error = this.handleError(err)
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')

      // Clean up headers in the API service
      api.clearToken()
    },

    handleError(err: unknown): string {
      if (axios.isAxiosError(err)) {
        const data = err.response?.data
        if (data && typeof data === 'object') {
          return Object.values(data).flat().join(', ')
        }
        return err.message
      }
      return 'An unexpected error occurred'
    },
  },
})
