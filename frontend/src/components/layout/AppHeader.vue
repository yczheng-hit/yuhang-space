<script setup>
import { useAuthStore } from '../../stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { ref } from 'vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mobileMenuOpen = ref(false)

const navItems = [
  { path: '/schedules', label: '日记', icon: '📖' },
  { path: '/recipes', label: '菜谱', icon: '🍳' },
  { path: '/chat', label: 'AI 助手', icon: '✨' },
]

function isActive(path) {
  return route.path.startsWith(path)
}

function handleLogout() {
  auth.logout()
  mobileMenuOpen.value = false
  router.push('/login')
}

function navigateTo(path) {
  mobileMenuOpen.value = false
  router.push(path)
}
</script>

<template>
  <header class="bg-white/60 backdrop-blur-xl shadow-lg shadow-indigo-500/5 border-b border-white/50 sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 h-14 sm:h-16 flex items-center justify-between">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2 group" @click="mobileMenuOpen = false">
        <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-xs sm:text-sm font-bold shadow-md shadow-violet-500/30">
          宇
        </div>
        <span class="text-lg sm:text-xl font-bold bg-gradient-to-r from-violet-600 via-fuchsia-600 to-pink-600 bg-clip-text text-transparent">
          寰宇智杭
        </span>
      </router-link>

      <!-- Desktop nav -->
      <nav class="hidden sm:flex items-center gap-1">
        <template v-if="auth.isAuthenticated">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 relative"
            :class="isActive(item.path)
              ? 'bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 text-violet-700 shadow-sm border border-violet-200/50'
              : 'text-gray-600 hover:text-violet-700 hover:bg-white/50'"
          >
            <span class="mr-1.5">{{ item.icon }}</span>
            {{ item.label }}
            <div v-if="isActive(item.path)" class="absolute -bottom-[1px] left-1/2 -translate-x-1/2 w-6 h-0.5 bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full"></div>
          </router-link>
          <div class="w-px h-6 bg-gray-200 mx-2"></div>
          <button
            @click="handleLogout"
            class="px-4 py-2 text-sm font-medium text-gray-500 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-all duration-300"
          >
            退出
          </button>
        </template>
        <template v-else>
          <router-link to="/login" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-violet-700 hover:bg-white/50 rounded-xl transition-all duration-300">登录</router-link>
          <router-link to="/register" class="px-5 py-2 text-sm font-medium bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-xl hover:from-violet-700 hover:to-fuchsia-700 transition-all duration-300 shadow-md shadow-violet-500/25">注册</router-link>
        </template>
      </nav>

      <!-- Mobile hamburger -->
      <button
        v-if="auth.isAuthenticated"
        @click="mobileMenuOpen = !mobileMenuOpen"
        class="sm:hidden w-10 h-10 flex items-center justify-center rounded-xl text-gray-600 hover:bg-white/50 transition-all"
      >
        <svg v-if="!mobileMenuOpen" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" /></svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>

      <!-- Mobile auth buttons (not logged in) -->
      <div v-if="!auth.isAuthenticated" class="flex sm:hidden items-center gap-2">
        <router-link to="/login" class="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-violet-700 rounded-lg transition-all">登录</router-link>
        <router-link to="/register" class="px-3 py-1.5 text-xs font-medium bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-lg shadow-sm">注册</router-link>
      </div>
    </div>

    <!-- Mobile dropdown menu -->
    <Transition name="slide-down">
      <div v-if="mobileMenuOpen && auth.isAuthenticated" class="sm:hidden bg-white/90 backdrop-blur-xl border-t border-white/50 shadow-lg">
        <div class="px-4 py-3 space-y-1">
          <button
            v-for="item in navItems"
            :key="item.path"
            @click="navigateTo(item.path)"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200"
            :class="isActive(item.path)
              ? 'bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 text-violet-700'
              : 'text-gray-600 hover:bg-gray-50'"
          >
            <span class="text-lg">{{ item.icon }}</span>
            {{ item.label }}
            <svg v-if="isActive(item.path)" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 ml-auto text-violet-500" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
          </button>
          <div class="border-t border-gray-100 my-2"></div>
          <button
            @click="handleLogout"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-rose-500 hover:bg-rose-50 transition-all duration-200"
          >
            <span class="text-lg">🚪</span>
            退出登录
          </button>
        </div>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
