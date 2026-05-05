<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const features = [
  { title: '日程管理', desc: '创建和管理您的日程安排', path: '/schedules', icon: '📅' },
  { title: '菜谱库', desc: '收藏和管理您的菜谱', path: '/recipes', icon: '🍳' },
  { title: 'AI 助手', desc: '智能对话，自动生成日程和菜谱', path: '/chat', icon: '🤖' },
]
</script>

<template>
  <div class="py-12">
    <h1 class="text-3xl font-bold text-center mb-2">欢迎使用寰宇智杭</h1>
    <p class="text-center text-gray-600 mb-12">您的智能生活管理平台</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
      <div
        v-for="feature in features"
        :key="feature.path"
        @click="router.push(feature.path)"
        class="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg transition-shadow"
      >
        <div class="text-4xl mb-4">{{ feature.icon }}</div>
        <h2 class="text-xl font-semibold mb-2">{{ feature.title }}</h2>
        <p class="text-gray-600">{{ feature.desc }}</p>
      </div>
    </div>
  </div>
</template>
