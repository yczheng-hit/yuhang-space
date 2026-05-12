import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(!!localStorage.getItem('access_token'))

  async function register(data) {
    const response = await authApi.register(data)
    return response.data
  }

  async function login(data) {
    const response = await authApi.login(data)
    const { access_token, refresh_token } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    isAuthenticated.value = true
    return response.data
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    isAuthenticated.value = false
  }

  return { isAuthenticated, register, login, logout }
})
