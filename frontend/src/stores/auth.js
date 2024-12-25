import { defineStore } from 'pinia'
import axios from 'axios'

// Add axios interceptor for authentication
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    
    hasRole: (state) => (role) => {
      return state.user?.roles?.includes(role) || false
    },
    
    hasPermission: (state) => (permission) => {
      return state.user?.permissions?.includes(permission) || false
    }
  },

  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('/api/auth/login', { username, password })
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem('access_token', this.token)
        return true
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },

    async logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
    },

    async fetchUser() {
      try {
        const response = await axios.get('/api/auth/me')
        this.user = response.data
        return true
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.logout()
        throw error
      }
    },

    async register(userData) {
      try {
        const response = await axios.post('/api/auth/register', userData)
        return response.data
      } catch (error) {
        console.error('Registration failed:', error)
        throw error
      }
    },

    async updateProfile(userData) {
      try {
        const response = await axios.put('/api/auth/me', userData)
        this.user = response.data
        return true
      } catch (error) {
        console.error('Profile update failed:', error)
        throw error
      }
    }
  }
}) 