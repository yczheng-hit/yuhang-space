<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const features = [
  {
    title: '生活日记',
    desc: '记录每天的生活点滴，支持图片视频，时间线回顾',
    path: '/schedules',
    gradient: 'from-violet-500 via-purple-500 to-fuchsia-500',
    shadow: 'shadow-violet-500/25',
    glow: 'group-hover:shadow-violet-500/40',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7 sm:w-8 sm:h-8"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>`,
    deco: '🌸',
  },
  {
    title: '菜谱库',
    desc: '收藏和管理您的菜谱，轻松记录烹饪灵感',
    path: '/recipes',
    gradient: 'from-amber-500 via-orange-500 to-rose-500',
    shadow: 'shadow-amber-500/25',
    glow: 'group-hover:shadow-amber-500/40',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7 sm:w-8 sm:h-8"><path stroke-linecap="round" stroke-linejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" /><path stroke-linecap="round" stroke-linejoin="round" d="M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z" /></svg>`,
    deco: '🍜',
  },
  {
    title: 'AI 助手',
    desc: '智能对话，自动生成日程和菜谱建议',
    path: '/chat',
    gradient: 'from-cyan-500 via-teal-500 to-emerald-500',
    shadow: 'shadow-cyan-500/25',
    glow: 'group-hover:shadow-cyan-500/40',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7 sm:w-8 sm:h-8"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>`,
    deco: '💫',
  },
]
</script>

<template>
  <div class="py-8 sm:py-12">
    <!-- Hero Section -->
    <div class="text-center mb-10 sm:mb-16 relative">
      <div class="absolute -top-4 left-1/2 -translate-x-1/2 text-4xl sm:text-6xl opacity-20 animate-float select-none pointer-events-none">✦</div>

      <h1 class="text-3xl sm:text-5xl font-extrabold mb-3 sm:mb-4 relative px-4">
        <span class="bg-gradient-to-r from-violet-600 via-fuchsia-600 to-pink-600 bg-clip-text text-transparent drop-shadow-sm">
          欢迎使用寰宇智杭
        </span>
      </h1>
      <p class="text-base sm:text-lg text-gray-500 max-w-md mx-auto leading-relaxed px-4">
        您的智能生活管理平台
        <span class="inline-block animate-bounce-slow">✨</span>
      </p>
      <div class="mt-5 sm:mt-6 mx-auto w-20 sm:w-24 h-1 bg-gradient-to-r from-violet-500 via-fuchsia-500 to-pink-500 rounded-full"></div>
    </div>

    <!-- Feature Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-5 sm:gap-8 max-w-5xl mx-auto px-2 sm:px-0">
      <div
        v-for="feature in features"
        :key="feature.path"
        @click="router.push(feature.path)"
        class="group relative cursor-pointer"
      >
        <div class="relative bg-white/70 backdrop-blur-md p-5 sm:p-8 rounded-2xl sm:rounded-3xl shadow-lg border border-white/80 transition-all duration-500 hover:shadow-2xl sm:hover:-translate-y-2 hover:bg-white/90 overflow-hidden active:scale-[0.98]"
             :class="[feature.shadow, feature.glow]">
          <div class="absolute top-0 right-0 w-24 sm:w-32 h-24 sm:h-32 opacity-10 transition-opacity duration-500 group-hover:opacity-20"
               :class="'bg-gradient-to-bl ' + feature.gradient"
               style="border-radius: 0 1.5rem 0 100%;"></div>

          <div class="w-12 h-12 sm:w-16 sm:h-16 rounded-xl sm:rounded-2xl bg-gradient-to-br flex items-center justify-center text-white mb-4 sm:mb-6 shadow-lg transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3"
               :class="[feature.gradient, feature.shadow]">
            <span v-html="feature.icon"></span>
          </div>

          <h2 class="text-lg sm:text-xl font-bold text-gray-800 mb-2 sm:mb-3 flex items-center gap-2">
            {{ feature.title }}
            <span class="text-base sm:text-lg opacity-60 group-hover:opacity-100 transition-opacity">{{ feature.deco }}</span>
          </h2>
          <p class="text-gray-500 leading-relaxed text-sm">{{ feature.desc }}</p>

          <div class="mt-4 sm:mt-6 flex items-center gap-2 text-sm font-medium text-gray-400 group-hover:text-violet-600 transition-colors duration-300">
            <span>开始使用</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
          </div>

          <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-500"
               :class="feature.gradient"></div>
        </div>
      </div>
    </div>

    <div class="text-center mt-10 sm:mt-16 text-gray-400 text-xs sm:text-sm px-4">
      <p>用科技记录生活 · 让每一天都有迹可循</p>
    </div>
  </div>
</template>

<style scoped>
@keyframes float {
  0%, 100% { transform: translate(-50%, 0); }
  50% { transform: translate(-50%, -10px); }
}
@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.animate-float { animation: float 3s ease-in-out infinite; }
.animate-bounce-slow { animation: bounce-slow 2s ease-in-out infinite; }
</style>
