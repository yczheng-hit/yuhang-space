<script setup>
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="bg-white shadow">
    <div class="container mx-auto px-4 py-4 flex items-center justify-between">
      <router-link to="/" class="text-xl font-bold text-gray-800">
        寰宇智杭
      </router-link>

      <nav class="flex items-center gap-4">
        <template v-if="auth.isAuthenticated">
          <router-link to="/schedules" class="text-gray-600 hover:text-gray-900">日程</router-link>
          <router-link to="/recipes" class="text-gray-600 hover:text-gray-900">菜谱</router-link>
          <router-link to="/chat" class="text-gray-600 hover:text-gray-900">AI 助手</router-link>
          <button
            @click="handleLogout"
            class="ml-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            退出
          </button>
        </template>
        <template v-else>
          <router-link to="/login" class="text-gray-600 hover:text-gray-900">登录</router-link>
          <router-link
            to="/register"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            注册
          </router-link>
        </template>
      </nav>
    </div>
  </header>
</template>
