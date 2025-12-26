import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || (null as string | null),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    loading: false,
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(credentials: any) {
      this.loading = true
      this.error = null
      try {
        const response = await api.login(credentials)

        const token = response.token
        const user = response.user

        this.token = token
        this.user = user

        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))

        return true
      } catch (err: any) {
        this.error = err.response?.data?.error || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async register(credentials: any) {
      this.loading = true
      this.error = null
      try {
        const response = await api.register(credentials)

        const token = response.token
        const user = response.user

        if (token) {
          this.token = token
          this.user = user
          localStorage.setItem('token', token)
          localStorage.setItem('user', JSON.stringify(user))
        }

        return true
      } catch (err: any) {
        const errors = err.response?.data
        this.error = Object.values(errors).flat().join(', ') || 'Registration failed'
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
    },
  },
})
