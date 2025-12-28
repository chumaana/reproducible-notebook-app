/**
 * Authentication Store
 * Manages user authentication state, login/register operations, and token persistence.
 */

import { defineStore } from 'pinia'
import api from '@/services/api'
import axios from 'axios'

interface User {
  id: number
  username: string
  email: string
}

interface LoginCredentials {
  username: string
  password: string
}

interface RegisterCredentials {
  username: string
  email: string
  password: string
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
    /**
     * Logs in a user with provided credentials.
     *
     * @param credentials - Username and password
     * @returns True if login successful, false otherwise
     */
    async login(credentials: LoginCredentials) {
      this.loading = true
      this.error = null

      try {
        const response = await api.login(credentials)
        this.token = response.token
        this.user = response.user

        // Persist to localStorage
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

    /**
     * Registers a new user account.
     *
     * @param credentials - Username, email, and password
     * @returns True if registration successful, false otherwise
     */
    async register(credentials: RegisterCredentials) {
      this.loading = true
      this.error = null

      try {
        const response = await api.register(credentials)

        if (response.token) {
          this.token = response.token
          this.user = response.user

          // Persist to localStorage
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

    /**
     * Logs out the current user and clears authentication state.
     */
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      api.clearToken()
    },

    /**
     * Clears the current error message.
     */
    clearError() {
      this.error = null
    },

    /**
     * Extracts error message from various error types.
     *
     * @param err - Error object
     * @returns Formatted error message string
     */
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
