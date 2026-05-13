<script setup>
import { ref, computed, onMounted } from 'vue'
import { useScheduleStore } from '../stores/schedule'
import { schedulesApi } from '../api/schedules'
import ScheduleFormModal from '../components/ScheduleFormModal.vue'
import MediaGallery from '../components/MediaGallery.vue'

const store = useScheduleStore()
const showModal = ref(false)
const editingEntry = ref(null)
const mediaMap = ref({})
const viewMode = ref('list')
const currentMonth = ref(new Date())
const selectedDate = ref(null)

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
  0: { emoji: '😊', label: '开心', color: 'border-l-amber-400', bg: 'bg-amber-50', gradient: 'from-amber-400 to-orange-400' },
  1: { emoji: '😌', label: '平静', color: 'border-l-sky-400', bg: 'bg-sky-50', gradient: 'from-sky-400 to-blue-400' },
  2: { emoji: '😢', label: '难过', color: 'border-l-slate-400', bg: 'bg-slate-50', gradient: 'from-slate-400 to-gray-400' },
  3: { emoji: '😤', label: '生气', color: 'border-l-rose-400', bg: 'bg-rose-50', gradient: 'from-rose-400 to-red-400' },
  4: { emoji: '🤔', label: '纠结', color: 'border-l-purple-400', bg: 'bg-purple-50', gradient: 'from-purple-400 to-violet-400' },
}

const timelineGroups = computed(() => {
  const groups = {}
  for (const entry of store.schedules) {
    const dateKey = new Date(entry.start_time).toLocaleDateString('zh-CN', {
      year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
    })
    if (!groups[dateKey]) groups[dateKey] = []
    groups[dateKey].push(entry)
  }
  return Object.entries(groups)
})

function getFirstImage(entry) {
  const media = mediaMap.value[entry.id]
  if (!media?.length) return null
  return media.find(m => m.file_type === 'image') || null
}

function truncate(text, len = 60) {
  if (!text) return ''
  return text.length > len ? text.slice(0, len) + '...' : text
}

function openCreate() {
  editingEntry.value = null
  showModal.value = true
}

function openEdit(entry) {
  editingEntry.value = entry
  showModal.value = true
}

async function handleSubmit(data, resolve) {
  let result
  if (editingEntry.value) {
    result = await store.updateSchedule(editingEntry.value.id, data)
    const { data: media } = await schedulesApi.listMedia(editingEntry.value.id)
    mediaMap.value[editingEntry.value.id] = media
  } else {
    result = await store.createSchedule(data)
    if (result?.id) {
      try {
        const { data: media } = await schedulesApi.listMedia(result.id)
        if (media.length) mediaMap.value[result.id] = media
      } catch {}
    }
  }
  if (resolve) resolve(result)
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
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

function formatTime(dateStr) {
  return new Date(dateStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function getMediaUrl(filePath) {
  return `/media/${filePath}`
}

// Calendar helpers
function toDateStr(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const holidays = {
  '2026-01-01': { name: '元旦', color: 'text-red-500' },
  '2026-02-16': { name: '除夕', color: 'text-red-500' },
  '2026-02-17': { name: '春节', color: 'text-red-500' },
  '2026-04-04': { name: '清明', color: 'text-gray-500' },
  '2026-05-01': { name: '劳动节', color: 'text-red-500' },
  '2026-06-19': { name: '端午', color: 'text-red-500' },
  '2026-09-25': { name: '中秋', color: 'text-red-500' },
  '2026-10-01': { name: '国庆', color: 'text-red-500' },
}

const entriesByDate = computed(() => {
  const map = {}
  for (const entry of store.schedules) {
    const key = toDateStr(new Date(entry.start_time))
    if (!map[key]) map[key] = []
    map[key].push(entry)
  }
  return map
})

const todayStr = computed(() => toDateStr(new Date()))

const calendarDays = computed(() => {
  const year = currentMonth.value.getFullYear()
  const month = currentMonth.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startDow = firstDay.getDay() // 0=Sun
  const totalDays = lastDay.getDate()

  const days = []

  // Previous month padding
  const prevLastDay = new Date(year, month, 0).getDate()
  for (let i = startDow - 1; i >= 0; i--) {
    const d = prevLastDay - i
    const date = new Date(year, month - 1, d)
    const dateStr = toDateStr(date)
    const dayEntries = entriesByDate.value[dateStr] || []
    days.push({ dateStr, day: d, isCurrentMonth: false, entries: dayEntries, holiday: holidays[dateStr] || null, moodEmoji: dayEntries.length ? moodMap[dayEntries[0].priority]?.emoji : null })
  }

  // Current month
  for (let d = 1; d <= totalDays; d++) {
    const date = new Date(year, month, d)
    const dateStr = toDateStr(date)
    const dayEntries = entriesByDate.value[dateStr] || []
    days.push({ dateStr, day: d, isCurrentMonth: true, entries: dayEntries, holiday: holidays[dateStr] || null, moodEmoji: dayEntries.length ? moodMap[dayEntries[0].priority]?.emoji : null })
  }

  // Next month padding to fill 6 rows (42 cells)
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    const date = new Date(year, month + 1, d)
    const dateStr = toDateStr(date)
    const dayEntries = entriesByDate.value[dateStr] || []
    days.push({ dateStr, day: d, isCurrentMonth: false, entries: dayEntries, holiday: holidays[dateStr] || null, moodEmoji: dayEntries.length ? moodMap[dayEntries[0].priority]?.emoji : null })
  }

  return days
})

const selectedDateEntries = computed(() => {
  if (!selectedDate.value) return []
  return entriesByDate.value[selectedDate.value] || []
})

const calendarTitle = computed(() => {
  return currentMonth.value.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })
})

function prevMonth() {
  const d = new Date(currentMonth.value)
  d.setMonth(d.getMonth() - 1)
  currentMonth.value = d
  selectedDate.value = null
}

function nextMonth() {
  const d = new Date(currentMonth.value)
  d.setMonth(d.getMonth() + 1)
  currentMonth.value = d
  selectedDate.value = null
}

function goToToday() {
  currentMonth.value = new Date()
  selectedDate.value = toDateStr(new Date())
}

function selectDate(dateStr) {
  selectedDate.value = selectedDate.value === dateStr ? null : dateStr
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 sm:mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">生活日记</h1>
        <p class="text-xs sm:text-sm text-gray-500 mt-1">记录生活的每一个美好瞬间 ✨</p>
      </div>
      <div class="flex items-center gap-2 sm:gap-3">
        <div class="flex bg-white/60 backdrop-blur-sm rounded-xl p-1 shadow-sm border border-white/80">
          <button
            @click="viewMode = 'list'"
            class="px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm rounded-lg transition-all duration-300"
            :class="viewMode === 'list' ? 'bg-white text-violet-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 sm:w-4 sm:h-4 inline mr-1 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" /></svg>
            列表
          </button>
          <button
            @click="viewMode = 'timeline'"
            class="px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm rounded-lg transition-all duration-300"
            :class="viewMode === 'timeline' ? 'bg-white text-violet-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 sm:w-4 sm:h-4 inline mr-1 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            时间线
          </button>
          <button
            @click="viewMode = 'calendar'"
            class="px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm rounded-lg transition-all duration-300"
            :class="viewMode === 'calendar' ? 'bg-white text-violet-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 sm:w-4 sm:h-4 inline mr-1 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" /></svg>
            日历
          </button>
        </div>
        <button
          @click="openCreate"
          class="flex-shrink-0 px-4 sm:px-5 py-2 sm:py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-xl hover:from-violet-700 hover:to-fuchsia-700 transition-all duration-300 shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 active:scale-95 font-medium text-xs sm:text-sm"
        >
          + 写日记
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="text-center py-12 sm:py-16">
      <div class="inline-block w-8 h-8 sm:w-10 sm:h-10 border-3 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>
      <p class="text-gray-500 mt-3 sm:mt-4 text-sm">加载中...</p>
    </div>

    <!-- Calendar View (always shows regardless of entries) -->
    <div v-else-if="viewMode === 'calendar'">
      <!-- Month navigation -->
      <div class="flex items-center justify-between mb-4 sm:mb-5 bg-white/60 backdrop-blur-sm rounded-xl sm:rounded-2xl p-3 sm:p-4 shadow-sm border border-white/80">
        <div class="flex items-center gap-2">
          <button
            @click="prevMonth"
            class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:text-violet-600 hover:bg-violet-50 transition-all duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
          </button>
          <h2 class="text-base sm:text-lg font-bold text-gray-800 min-w-[140px] text-center">{{ calendarTitle }}</h2>
          <button
            @click="nextMonth"
            class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:text-violet-600 hover:bg-violet-50 transition-all duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
          </button>
        </div>
        <button
          @click="goToToday"
          class="px-3 py-1.5 text-xs font-medium text-violet-600 bg-violet-50 hover:bg-violet-100 rounded-lg transition-all duration-200 border border-violet-100"
        >
          今天
        </button>
      </div>

      <!-- Calendar grid -->
      <div class="bg-white/60 backdrop-blur-sm rounded-xl sm:rounded-2xl shadow-sm border border-white/80 overflow-hidden">
        <div class="grid grid-cols-7 border-b border-gray-100">
          <div v-for="w in ['日','一','二','三','四','五','六']" :key="w" class="py-2 sm:py-2.5 text-center text-[10px] sm:text-xs font-medium text-gray-400">
            {{ w }}
          </div>
        </div>
        <div class="grid grid-cols-7">
          <div
            v-for="(cell, idx) in calendarDays"
            :key="idx"
            @click="selectDate(cell.dateStr)"
            class="relative aspect-square flex flex-col items-center justify-center cursor-pointer transition-all duration-200 border-b border-r border-gray-50/80 hover:bg-violet-50/50"
            :class="[
              cell.dateStr === selectedDate ? 'bg-gradient-to-br from-violet-100 to-fuchsia-100' : '',
              !cell.isCurrentMonth ? 'opacity-30' : '',
            ]"
          >
            <!-- Mood emoji -->
            <span v-if="cell.moodEmoji" class="text-[10px] sm:text-xs leading-none mb-0.5">{{ cell.moodEmoji }}</span>
            <span
              class="text-xs sm:text-sm font-medium leading-none"
              :class="[
                cell.dateStr === todayStr ? 'text-violet-600 font-bold' : cell.isCurrentMonth ? 'text-gray-700' : 'text-gray-400',
                cell.dateStr === selectedDate ? 'text-violet-700' : '',
              ]"
            >
              {{ cell.day }}
            </span>
            <!-- Holiday label -->
            <span v-if="cell.holiday" class="text-[8px] sm:text-[10px] leading-tight mt-0.5 font-medium" :class="cell.holiday.color">
              {{ cell.holiday.name }}
            </span>
            <!-- Dot indicators for multiple entries -->
            <div v-if="cell.entries.length > 1" class="flex gap-0.5 mt-0.5">
              <div
                v-for="n in Math.min(cell.entries.length, 3)"
                :key="n"
                class="w-1 h-1 rounded-full"
                :class="cell.dateStr === selectedDate ? 'bg-fuchsia-500' : 'bg-violet-400'"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Selected date entries -->
      <div v-if="selectedDate" class="mt-4 sm:mt-5">
        <h3 class="text-sm sm:text-base font-bold text-gray-700 mb-3">
          {{ selectedDate }} — {{ selectedDateEntries.length }} 篇日记
        </h3>
        <div v-if="selectedDateEntries.length === 0" class="text-center py-8 bg-white/50 backdrop-blur-sm rounded-xl sm:rounded-2xl border border-white/80 shadow-sm">
          <p class="text-gray-400 text-sm">这一天还没有日记</p>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="entry in selectedDateEntries"
            :key="entry.id"
            class="relative bg-white/70 backdrop-blur-sm rounded-xl sm:rounded-2xl p-3.5 sm:p-5 shadow-md border border-white/80 hover:shadow-xl active:scale-[0.99] transition-all duration-500 cursor-pointer group"
            @click="openEdit(entry)"
          >
            <div class="flex items-start gap-2 sm:gap-3">
              <span class="text-lg sm:text-2xl flex-shrink-0">{{ moodMap[entry.priority]?.emoji }}</span>
              <div class="flex-1 min-w-0">
                <h4 class="font-bold text-gray-800 text-sm sm:text-base mb-1 sm:mb-1.5">{{ entry.title }}</h4>
                <p v-if="entry.description" class="text-xs sm:text-sm text-gray-500 line-clamp-2 leading-relaxed">
                  {{ truncate(entry.description) }}
                </p>
                <div class="flex items-center gap-2 mt-2 sm:mt-3 flex-wrap">
                  <span class="text-[10px] sm:text-xs text-gray-400">{{ formatTime(entry.start_time) }}</span>
                  <div v-if="entry.tags?.length" class="flex gap-1">
                    <span
                      v-for="tag in entry.tags.slice(0, 2)"
                      :key="tag"
                      class="px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs bg-gradient-to-r from-violet-50 to-fuchsia-50 text-violet-600 rounded-full border border-violet-100"
                    >{{ tag }}</span>
                  </div>
                  <span v-if="mediaMap[entry.id]?.length" class="text-[10px] sm:text-xs text-gray-400">
                    {{ mediaMap[entry.id].length }} 个媒体
                  </span>
                </div>
              </div>
              <div v-if="getFirstImage(entry)" class="w-12 h-12 sm:w-16 sm:h-16 rounded-lg sm:rounded-xl overflow-hidden flex-shrink-0 shadow-sm">
                <img :src="getMediaUrl(getFirstImage(entry).file_path)" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
              </div>
            </div>
            <div class="absolute top-2 right-2 sm:top-3 sm:right-3 flex gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-300">
              <button
                @click.stop="openEdit(entry)"
                class="w-6 h-6 sm:w-7 sm:h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-violet-600 hover:bg-violet-50 transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>
              </button>
              <button
                @click.stop="handleDelete(entry.id)"
                class="w-6 h-6 sm:w-7 sm:h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state (only for list/timeline) -->
    <div v-else-if="store.schedules.length === 0" class="text-center py-12 sm:py-20 bg-white/50 backdrop-blur-sm rounded-2xl sm:rounded-3xl border border-white/80 shadow-lg">
      <div class="text-5xl sm:text-6xl mb-4 animate-bounce-slow">📝</div>
      <p class="text-gray-600 text-base sm:text-lg font-medium mb-2">还没有日记</p>
      <p class="text-gray-400 text-xs sm:text-sm">点击上方按钮开始记录生活吧~</p>
    </div>

    <!-- List View -->
    <div v-else-if="viewMode === 'list'" class="space-y-3 sm:space-y-4">
      <div
        v-for="entry in store.schedules"
        :key="entry.id"
        class="bg-white/70 backdrop-blur-sm rounded-xl sm:rounded-2xl shadow-md hover:shadow-xl transition-all duration-500 border border-white/80 overflow-hidden group active:scale-[0.99]"
      >
        <div class="flex">
          <!-- Thumbnail - mobile: smaller -->
          <div class="w-16 h-16 sm:w-28 sm:h-28 flex-shrink-0 m-3 sm:m-4 rounded-lg sm:rounded-xl overflow-hidden shadow-sm">
            <img
              v-if="getFirstImage(entry)"
              :src="getMediaUrl(getFirstImage(entry).file_path)"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            />
            <div
              v-else
              class="w-full h-full flex items-center justify-center text-2xl sm:text-4xl bg-gradient-to-br"
              :class="moodMap[entry.priority]?.gradient || 'from-gray-200 to-gray-300'"
            >
              <span class="drop-shadow-sm">{{ moodMap[entry.priority]?.emoji || '📝' }}</span>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0 py-3 pr-3 sm:py-4 sm:pr-4">
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1.5 sm:gap-2 mb-1">
                  <span class="text-base sm:text-lg">{{ moodMap[entry.priority]?.emoji }}</span>
                  <h3 class="text-sm sm:text-base font-bold text-gray-800 truncate">{{ entry.title }}</h3>
                </div>
                <p v-if="entry.description" class="text-gray-500 text-xs sm:text-sm line-clamp-2 mb-2 sm:mb-2.5 leading-relaxed">{{ entry.description }}</p>

                <div class="flex items-center gap-2 sm:gap-3 flex-wrap">
                  <span class="text-[10px] sm:text-xs text-gray-400 flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" /></svg>
                    <span class="hidden sm:inline">{{ formatDate(entry.start_time) }}</span>
                    <span class="sm:hidden">{{ formatDate(entry.start_time).replace('年', '/').replace('月', '/').replace('日', '') }}</span>
                    {{ formatTime(entry.start_time) }}
                  </span>
                  <div v-if="entry.tags?.length" class="flex gap-1 flex-wrap">
                    <span
                      v-for="tag in entry.tags.slice(0, 3)"
                      :key="tag"
                      class="px-1.5 sm:px-2.5 py-0.5 text-[10px] sm:text-xs bg-gradient-to-r from-violet-50 to-fuchsia-50 text-violet-600 rounded-full border border-violet-100"
                    >
                      {{ tag }}
                    </span>
                    <span v-if="entry.tags.length > 3" class="text-[10px] sm:text-xs text-gray-400">+{{ entry.tags.length - 3 }}</span>
                  </div>
                  <span v-if="mediaMap[entry.id]?.length" class="text-[10px] sm:text-xs text-gray-400 flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v13.5A1.5 1.5 0 003.75 21z" /></svg>
                    {{ mediaMap[entry.id].length }}
                  </span>
                </div>
              </div>

              <!-- Actions: mobile always visible, desktop on hover -->
              <div class="flex items-center gap-0.5 sm:gap-1 ml-2 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-300 flex-shrink-0">
                <button
                  @click="openEdit(entry)"
                  class="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-violet-600 hover:bg-violet-50 transition-all duration-200"
                  title="编辑"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>
                </button>
                <button
                  @click="handleDelete(entry.id)"
                  class="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-all duration-200"
                  title="删除"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="mediaMap[entry.id]?.length" class="px-3 pb-3 sm:px-4 sm:pb-4">
          <MediaGallery :media="mediaMap[entry.id]" />
        </div>
      </div>
    </div>

    <!-- Timeline View -->
    <div v-else-if="viewMode === 'timeline'" class="relative">
      <!-- Vertical gradient line -->
      <div class="absolute left-4 sm:left-[19px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-violet-300 via-fuchsia-300 to-pink-300"></div>

      <div v-for="([dateLabel, entries], groupIdx) in timelineGroups" :key="dateLabel" class="mb-8 sm:mb-10">
        <!-- Date header -->
        <div class="flex items-center gap-3 sm:gap-4 mb-4 sm:mb-5 relative">
          <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-[10px] sm:text-xs font-bold z-10 shadow-lg shadow-violet-500/30">
            {{ new Date(entries[0].start_time).getDate() }}
          </div>
          <div>
            <h3 class="text-sm sm:text-base font-bold text-gray-800">{{ dateLabel }}</h3>
            <p class="text-[10px] sm:text-xs text-gray-400">{{ entries.length }} 篇日记</p>
          </div>
        </div>

        <!-- Entries -->
        <div class="ml-4 sm:ml-[19px] pl-5 sm:pl-8 space-y-2 sm:space-y-3">
          <div
            v-for="entry in entries"
            :key="entry.id"
            class="relative bg-white/70 backdrop-blur-sm rounded-xl sm:rounded-2xl p-3.5 sm:p-5 shadow-md border border-white/80 hover:shadow-xl active:scale-[0.99] sm:hover:-translate-y-0.5 transition-all duration-500 cursor-pointer group"
            @click="openEdit(entry)"
          >
            <!-- Dot on timeline -->
            <div class="absolute -left-[21px] sm:-left-[33px] top-4 sm:top-6 w-2.5 h-2.5 sm:w-3.5 sm:h-3.5 rounded-full bg-white border-2 border-fuchsia-400 shadow-sm shadow-fuchsia-400/30"></div>

            <div class="flex items-start gap-2 sm:gap-3">
              <span class="text-lg sm:text-2xl flex-shrink-0">{{ moodMap[entry.priority]?.emoji }}</span>
              <div class="flex-1 min-w-0">
                <h4 class="font-bold text-gray-800 text-sm sm:text-base mb-1 sm:mb-1.5">{{ entry.title }}</h4>
                <p v-if="entry.description" class="text-xs sm:text-sm text-gray-500 line-clamp-2 leading-relaxed">
                  {{ truncate(entry.description) }}
                </p>
                <div class="flex items-center gap-2 mt-2 sm:mt-3 flex-wrap">
                  <span class="text-[10px] sm:text-xs text-gray-400">{{ formatTime(entry.start_time) }}</span>
                  <div v-if="entry.tags?.length" class="flex gap-1">
                    <span
                      v-for="tag in entry.tags.slice(0, 2)"
                      :key="tag"
                      class="px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs bg-gradient-to-r from-violet-50 to-fuchsia-50 text-violet-600 rounded-full border border-violet-100"
                    >{{ tag }}</span>
                  </div>
                  <span v-if="mediaMap[entry.id]?.length" class="text-[10px] sm:text-xs text-gray-400">
                    {{ mediaMap[entry.id].length }} 个媒体
                  </span>
                </div>
              </div>

              <!-- Thumbnail -->
              <div v-if="getFirstImage(entry)" class="w-12 h-12 sm:w-16 sm:h-16 rounded-lg sm:rounded-xl overflow-hidden flex-shrink-0 shadow-sm">
                <img :src="getMediaUrl(getFirstImage(entry).file_path)" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
              </div>
            </div>

            <!-- Actions -->
            <div class="absolute top-2 right-2 sm:top-3 sm:right-3 flex gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-300">
              <button
                @click.stop="openEdit(entry)"
                class="w-6 h-6 sm:w-7 sm:h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-violet-600 hover:bg-violet-50 transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>
              </button>
              <button
                @click.stop="handleDelete(entry.id)"
                class="w-6 h-6 sm:w-7 sm:h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
              </button>
            </div>
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

<style scoped>
@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.animate-bounce-slow { animation: bounce-slow 2s ease-in-out infinite; }
</style>
