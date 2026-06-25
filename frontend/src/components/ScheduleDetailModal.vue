<script setup>
import { ref, onMounted } from 'vue'
import { schedulesApi } from '../api/schedules'
import MediaGallery from './MediaGallery.vue'

const props = defineProps({
  entry: { type: Object, required: true },
})

const emit = defineEmits(['close', 'edit', 'delete'])

const mediaList = ref([])

const moodMap = {
  0: { emoji: '😊', label: '开心', color: 'bg-amber-50 border-amber-200', text: 'text-amber-700' },
  1: { emoji: '😌', label: '平静', color: 'bg-sky-50 border-sky-200', text: 'text-sky-700' },
  2: { emoji: '😢', label: '难过', color: 'bg-slate-50 border-slate-200', text: 'text-slate-700' },
  3: { emoji: '😤', label: '生气', color: 'bg-rose-50 border-rose-200', text: 'text-rose-700' },
  4: { emoji: '🤔', label: '纠结', color: 'bg-purple-50 border-purple-200', text: 'text-purple-700' },
}

const mood = moodMap[props.entry.priority] || moodMap[1]

onMounted(async () => {
  try {
    const { data } = await schedulesApi.listMedia(props.entry.id)
    mediaList.value = data
  } catch {}
})

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
  })
}

function formatTime(dateStr) {
  return new Date(dateStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatCreatedAt(dateStr) {
  if (!dateStr) return ''
  // created_at is stored as UTC, convert to UTC+8
  const d = new Date(dateStr + (dateStr.includes('Z') || dateStr.includes('+') ? '' : 'Z'))
  const pad = n => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 backdrop-blur-md flex items-end sm:items-center justify-center z-50 animate-fade-in" @click.self="emit('close')">
    <div class="bg-white w-full sm:max-w-lg sm:rounded-3xl rounded-t-3xl shadow-2xl max-h-[92vh] sm:max-h-[90vh] overflow-y-auto animate-slide-up sm:animate-scale-in">
      <!-- Drag handle mobile -->
      <div class="flex justify-center pt-3 sm:hidden">
        <div class="w-10 h-1 bg-gray-300 rounded-full"></div>
      </div>

      <!-- Header -->
      <div class="sticky top-0 bg-white/90 backdrop-blur-xl z-10 flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <div class="flex items-center gap-2 min-w-0">
          <span class="text-xl">{{ mood.emoji }}</span>
          <h2 class="text-lg font-bold text-gray-800 truncate">{{ entry.title }}</h2>
        </div>
        <button @click="emit('close')" class="w-8 h-8 flex items-center justify-center rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all text-xl flex-shrink-0">&times;</button>
      </div>

      <div class="p-5 space-y-5">
        <!-- Meta info -->
        <div class="flex flex-wrap gap-2">
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm" :class="[mood.color, mood.text]">
            {{ mood.emoji }} {{ mood.label }}
          </span>
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-50 border border-gray-200 text-sm text-gray-600">
            📅 {{ formatDate(entry.start_time) }}
          </span>
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-50 border border-gray-200 text-sm text-gray-600">
            🕐 {{ formatTime(entry.start_time) }}
          </span>
          <span v-if="entry.created_at" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-50 border border-gray-200 text-sm text-gray-400">
            ✏️ 添加于 {{ formatCreatedAt(entry.created_at) }}
          </span>
        </div>

        <!-- Tags -->
        <div v-if="entry.tags?.length" class="flex flex-wrap gap-2">
          <span
            v-for="tag in entry.tags"
            :key="tag"
            class="px-2.5 py-1 text-xs bg-gradient-to-r from-violet-50 to-fuchsia-50 text-violet-700 rounded-full border border-violet-100"
          >
            {{ tag }}
          </span>
        </div>

        <!-- Content -->
        <div v-if="entry.description">
          <h3 class="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <span class="w-1 h-4 bg-gradient-to-b from-violet-400 to-fuchsia-500 rounded-full"></span>
            日记内容
          </h3>
          <div class="bg-gray-50 rounded-2xl p-4">
            <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ entry.description }}</p>
          </div>
        </div>

        <!-- Media -->
        <div v-if="mediaList.length">
          <h3 class="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <span class="w-1 h-4 bg-gradient-to-b from-cyan-400 to-blue-500 rounded-full"></span>
            媒体文件
          </h3>
          <MediaGallery :media="mediaList" />
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-2 pb-1">
          <button
            @click="emit('edit', entry)"
            class="flex-1 py-2.5 border border-violet-200 text-violet-600 rounded-xl hover:bg-violet-50 transition-all text-sm font-medium"
          >
            编辑
          </button>
          <button
            @click="emit('delete', entry.id)"
            class="flex-1 py-2.5 border border-rose-200 text-rose-500 rounded-xl hover:bg-rose-50 transition-all text-sm font-medium"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fade-in 0.25s ease-out; }
.animate-slide-up { animation: slide-up 0.35s cubic-bezier(0.16, 1, 0.3, 1); }
.animate-scale-in { animation: scale-in 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes slide-up { from { opacity: 0; transform: translateY(100%); } to { opacity: 1; transform: translateY(0); } }
@keyframes scale-in { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
