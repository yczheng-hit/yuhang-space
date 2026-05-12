<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(form.value)
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-10 sm:mt-20 relative px-4 sm:px-0">
    <div class="absolute -top-8 -right-8 w-16 h-16 rounded-full bg-gradient-to-br from-pink-400/20 to-rose-400/20 blur-xl animate-pulse-slow hidden sm:block"></div>
    <div class="absolute -bottom-8 -left-8 w-20 h-20 rounded-full bg-gradient-to-br from-violet-400/20 to-purple-400/20 blur-xl animate-pulse-slow animation-delay-1000 hidden sm:block"></div>

    <div class="text-center mb-6 sm:mb-8">
      <div class="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-fuchsia-500 to-pink-500 shadow-lg shadow-fuchsia-500/30 mb-3 sm:mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 sm:w-8 sm:h-8 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.766z" /></svg>
      </div>
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-800 mb-1 sm:mb-2">创建账户</h1>
      <p class="text-sm text-gray-500">注册开始使用智能生活管理平台</p>
    </div>

    <form @submit.prevent="handleRegister" class="bg-white/70 backdrop-blur-xl p-6 sm:p-8 rounded-2xl sm:rounded-3xl shadow-xl shadow-fuchsia-500/5 border border-white/80 relative overflow-hidden">
      <div class="absolute top-0 left-0 w-40 h-40 bg-gradient-to-br from-fuchsia-500/5 to-pink-500/5 rounded-br-full"></div>

      <div v-if="error" class="mb-4 sm:mb-5 p-3 bg-rose-50 text-rose-700 rounded-xl text-sm border border-rose-100 relative z-10">{{ error }}</div>

      <div class="mb-4 sm:mb-5 relative z-10">
        <label class="block text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">用户名</label>
        <input
          v-model="form.username"
          type="text"
          required
          minlength="2"
          maxlength="50"
          placeholder="2-50 个字符"
          class="w-full px-4 py-2.5 sm:py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-fuchsia-500/50 focus:border-fuchsia-400 transition-all duration-300 bg-white/50 focus:bg-white shadow-sm text-sm sm:text-base"
        />
      </div>

      <div class="mb-5 sm:mb-6 relative z-10">
        <label class="block text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">密码</label>
        <input
          v-model="form.password"
          type="password"
          required
          minlength="6"
          placeholder="至少 6 位，包含字母和数字"
          class="w-full px-4 py-2.5 sm:py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-fuchsia-500/50 focus:border-fuchsia-400 transition-all duration-300 bg-white/50 focus:bg-white shadow-sm text-sm sm:text-base"
        />
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="relative z-10 w-full py-2.5 sm:py-3 bg-gradient-to-r from-fuchsia-600 to-pink-600 text-white rounded-xl hover:from-fuchsia-700 hover:to-pink-700 disabled:opacity-50 font-medium transition-all duration-300 shadow-lg shadow-fuchsia-500/25 hover:shadow-xl hover:shadow-fuchsia-500/30 active:scale-[0.98] text-sm sm:text-base"
      >
        <span v-if="loading" class="flex items-center justify-center gap-2">
          <svg class="animate-spin w-4 h-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
          注册中...
        </span>
        <span v-else>注册</span>
      </button>

      <p class="mt-5 sm:mt-6 text-center text-sm text-gray-500 relative z-10">
        已有账户？
        <router-link to="/login" class="text-fuchsia-600 font-medium hover:text-violet-600 transition-colors">登录</router-link>
      </p>
    </form>
  </div>
</template>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}
.animate-pulse-slow { animation: pulse-slow 4s ease-in-out infinite; }
.animation-delay-1000 { animation-delay: 1s; }
</style>
