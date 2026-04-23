import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => localStorage.getItem('is_admin') === 'true')

  async function login(credentials) {
    loading.value = true
    try {
      const response = await authAPI.login(credentials)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('token', response.access_token)
      if (response.user?.is_admin) {
        localStorage.setItem('is_admin', 'true')
      }
      return response
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    try {
      const response = await authAPI.register(userData)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('token', response.access_token)
      return response
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return null
    try {
      const response = await authAPI.getMe()
      user.value = response
      if (response.is_admin) {
        localStorage.setItem('is_admin', 'true')
      }
      return response
    } catch (error) {
      logout()
      return null
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('is_admin')
  }

  return {
    token,
    user,
    loading,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchUser,
    logout
  }
})
