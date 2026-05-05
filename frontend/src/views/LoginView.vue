<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-16">
    <h1 class="text-2xl font-bold mb-6 text-center">登录</h1>

    <form @submit.prevent="handleLogin" class="bg-white p-6 rounded-lg shadow">
      <div v-if="error" class="mb-4 p-3 bg-red-100 text-red-700 rounded">{{ error }}</div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">用户名 / 邮箱</label>
        <input
          v-model="form.username"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
        <input
          v-model="form.password"
          type="password"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>

      <p class="mt-4 text-center text-sm text-gray-600">
        还没有账户？
        <router-link to="/register" class="text-blue-500 hover:underline">注册</router-link>
      </p>
    </form>
  </div>
</template>
