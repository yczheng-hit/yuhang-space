<script setup>
import { ref, onMounted } from 'vue'
import { useScheduleStore } from '../stores/schedule'
import { schedulesApi } from '../api/schedules'
import ScheduleFormModal from '../components/ScheduleFormModal.vue'
import MediaGallery from '../components/MediaGallery.vue'

const store = useScheduleStore()
const showModal = ref(false)
const editingEntry = ref(null)
const mediaMap = ref({})

onMounted(async () => {
  await store.fetchSchedules()
  for (const entry of store.schedules) {
    try {
      const { data } = await schedulesApi.listMedia(entry.id)
      if (data.length) mediaMap.value[entry.id] = data
    } catch {}
  }
})

const moodMap = {
  0: { emoji: '😊', label: '开心' },
  1: { emoji: '😐', label: '平静' },
  2: { emoji: '😢', label: '难过' },
  3: { emoji: '😡', label: '生气' },
  4: { emoji: '🤔', label: '纠结' },
}

function openCreate() {
  editingEntry.value = null
  showModal.value = true
}

function openEdit(entry) {
  editingEntry.value = entry
  showModal.value = true
}

async function handleSubmit(data) {
  if (editingEntry.value) {
    await store.updateSchedule(editingEntry.value.id, data)
    const { data: media } = await schedulesApi.listMedia(editingEntry.value.id)
    mediaMap.value[editingEntry.value.id] = media
  } else {
    await store.createSchedule(data)
  }
  showModal.value = false
  editingEntry.value = null
}

async function handleDelete(id) {
  if (confirm('确定删除这篇日记？')) {
    await store.deleteSchedule(id)
    delete mediaMap.value[id]
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

function formatTime(dateStr) {
  return new Date(dateStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">生活日记</h1>
      <button
        @click="openCreate"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        + 写日记
      </button>
    </div>

    <div v-if="store.loading" class="text-center py-8 text-gray-500">加载中...</div>

    <div v-else-if="store.schedules.length === 0" class="text-center py-12 text-gray-400">
      还没有日记，点击上方按钮开始记录
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="entry in store.schedules"
        :key="entry.id"
        class="bg-white p-5 rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <span v-if="moodMap[entry.priority]" class="text-2xl">{{ moodMap[entry.priority].emoji }}</span>
              <h3 class="text-lg font-semibold">{{ entry.title }}</h3>
            </div>
            <p v-if="entry.description" class="text-gray-600 whitespace-pre-line">{{ entry.description }}</p>

            <!-- 媒体展示 -->
            <div v-if="mediaMap[entry.id]?.length" class="mt-3">
              <MediaGallery :media="mediaMap[entry.id]" />
            </div>

            <div class="flex items-center gap-4 mt-3">
              <span class="text-sm text-gray-400">
                {{ formatDate(entry.start_time) }} {{ formatTime(entry.start_time) }}
              </span>
              <div v-if="entry.tags?.length" class="flex gap-1 flex-wrap">
                <span
                  v-for="tag in entry.tags"
                  :key="tag"
                  class="px-2 py-0.5 text-xs bg-gray-100 text-gray-500 rounded"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-1 ml-4 flex-shrink-0">
            <button
              @click="openEdit(entry)"
              class="text-gray-300 hover:text-blue-500 text-lg px-1"
              title="编辑"
            >
              ✎
            </button>
            <button
              @click="handleDelete(entry.id)"
              class="text-gray-300 hover:text-red-500 text-xl px-1"
              title="删除"
            >
              &times;
            </button>
          </div>
        </div>
      </div>
    </div>

    <ScheduleFormModal
      v-if="showModal"
      :entry="editingEntry"
      @close="showModal = false; editingEntry = null"
      @submit="handleSubmit"
    />
  </div>
</template>
