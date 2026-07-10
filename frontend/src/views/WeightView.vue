<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useWeightStore } from '../stores/weight'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const store = useWeightStore()
const showProfileModal = ref(false)
const showRecordModal = ref(false)
const editingRecord = ref(null)
const editingProfile = ref(null)
const profileForm = ref({ name: '', color: '#8b5cf6', height: null, target_weight: null })
const recordForm = ref({ weight: null, date: new Date().toISOString().slice(0, 10), note: '' })
const chartRef = ref(null)
const quickWeight = ref(null)
const timeRange = ref('all')
const compareMode = ref(false)
const compareSet = ref(new Set())
let chartInstance = null

const rangeOptions = [
  { label: '7天', value: '7d' },
  { label: '30天', value: '30d' },
  { label: '90天', value: '90d' },
  { label: '半年', value: '180d' },
  { label: '全部', value: 'all' },
]

const colorOptions = [
  { label: '紫色', value: '#8b5cf6' },
  { label: '蓝色', value: '#3b82f6' },
  { label: '绿色', value: '#10b981' },
  { label: '红色', value: '#ef4444' },
  { label: '橙色', value: '#f59e0b' },
  { label: '粉色', value: '#ec4899' },
]

const activeProfile = computed(() => {
  return store.profiles.find(p => p.id === store.activeProfileId) || null
})

const stats = computed(() => {
  const recs = store.records
  if (!recs.length) return null
  const sorted = [...recs].sort((a, b) => a.date.localeCompare(b.date))
  const latest = sorted[sorted.length - 1]
  const prev = sorted.length >= 2 ? sorted[sorted.length - 2] : null
  const change = prev ? +(latest.weight - prev.weight).toFixed(1) : 0
  const weights = sorted.map(r => r.weight)
  const profile = activeProfile.value
  let bmi = null, bmiCategory = ''
  if (profile?.height) {
    const h = profile.height / 100
    bmi = +(latest.weight / (h * h)).toFixed(1)
    if (bmi < 18.5) bmiCategory = '偏瘦'
    else if (bmi < 24) bmiCategory = '正常'
    else if (bmi < 28) bmiCategory = '偏胖'
    else bmiCategory = '肥胖'
  }
  let targetProgress = null
  if (profile?.target_weight) {
    const start = sorted[0].weight
    const target = profile.target_weight
    const total = Math.abs(start - target)
    const done = Math.abs(start - latest.weight)
    targetProgress = total > 0 ? Math.min(100, Math.round((done / total) * 100)) : 100
  }
  return { current: latest.weight, change, min: Math.min(...weights), max: Math.max(...weights), days: recs.length, bmi, bmiCategory, targetProgress, targetWeight: profile?.target_weight }
})

const filteredRecords = computed(() => {
  if (timeRange.value === 'all') return store.records
  const days = parseInt(timeRange.value)
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - days)
  const cutoffStr = cutoff.toLocaleDateString('sv-SE')
  return store.records.filter(r => r.date >= cutoffStr)
})

const chartData = computed(() => {
  const sorted = [...filteredRecords.value].sort((a, b) => a.date.localeCompare(b.date))
  return {
    labels: sorted.map(r => r.date.slice(5)),
    values: sorted.map(r => r.weight),
  }
})

watch(() => store.activeProfileId, () => {
  nextTick(renderChart)
})

watch(chartData, () => {
  nextTick(renderChart)
}, { deep: true })

function renderChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
  if (!chartRef.value || !chartData.value.labels.length) return

  const ctx = chartRef.value.getContext('2d')
  const color = activeProfile.value?.color || '#8b5cf6'

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.value.labels,
      datasets: [{
        label: '体重 (kg)',
        data: chartData.value.values,
        borderColor: color,
        backgroundColor: color + '20',
        borderWidth: 2.5,
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: color,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.parsed.y} kg`,
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } },
        },
        y: {
          beginAtZero: false,
          grid: { color: '#f3f4f6' },
          ticks: {
            font: { size: 11 },
            callback: (v) => v + ' kg',
          },
        },
      },
    },
  })
}

onMounted(async () => {
  await store.fetchProfiles()
  if (store.activeProfileId) {
    await store.fetchRecords(store.activeProfileId)
  }
})

function selectProfile(id) {
  store.setActiveProfile(id)
}

function openCreateProfile() {
  editingProfile.value = null
  profileForm.value = { name: '', color: '#8b5cf6', height: null, target_weight: null }
  showProfileModal.value = true
}

function openEditProfile(profile) {
  editingProfile.value = profile
  profileForm.value = {
    name: profile.name,
    color: profile.color || '#8b5cf6',
    height: profile.height,
    target_weight: profile.target_weight,
  }
  showProfileModal.value = true
}

async function handleSaveProfile() {
  if (!profileForm.value.name.trim()) return
  if (editingProfile.value) {
    await store.updateProfile(editingProfile.value.id, profileForm.value)
  } else {
    await store.createProfile(profileForm.value)
  }
  showProfileModal.value = false
}

async function handleDeleteProfile(id) {
  if (confirm('确定删除此角色及其所有体重记录？')) {
    await store.deleteProfile(id)
  }
}

async function handleQuickRecord() {
  if (!quickWeight.value || !store.activeProfileId) return
  await store.createRecord(store.activeProfileId, {
    weight: quickWeight.value,
    date: new Date().toISOString().slice(0, 10),
    note: null,
  })
  quickWeight.value = null
}

async function toggleCompare() {
  compareMode.value = !compareMode.value
  if (compareMode.value) {
    compareSet.value = new Set(store.profiles.map(p => p.id))
    await store.fetchAllRecords()
    renderCompareChart()
  } else {
    renderChart()
  }
}

function toggleCompareProfile(id) {
  const s = new Set(compareSet.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  compareSet.value = s
  renderCompareChart()
}

function renderCompareChart() {
  if (chartInstance) { chartInstance.destroy(); chartInstance = null }
  if (!chartRef.value) return
  const datasets = []
  for (const pid of compareSet.value) {
    const profile = store.profiles.find(p => p.id === pid)
    const recs = (store.allRecords[pid] || []).sort((a, b) => a.date.localeCompare(b.date))
    if (recs.length === 0) continue
    datasets.push({
      label: profile?.name || pid,
      data: recs.map(r => r.weight),
      borderColor: profile?.color || '#8b5cf6',
      backgroundColor: (profile?.color || '#8b5cf6') + '15',
      borderWidth: 2,
      fill: false,
      tension: 0.3,
      pointRadius: 3,
      pointBackgroundColor: profile?.color || '#8b5cf6',
      pointBorderColor: '#fff',
      pointBorderWidth: 1.5,
    })
  }
  if (datasets.length === 0) return
  // Use union of all dates as labels
  const allDates = new Set()
  for (const pid of compareSet.value) {
    (store.allRecords[pid] || []).forEach(r => allDates.add(r.date))
  }
  const labels = [...allDates].sort().map(d => d.slice(5))
  const ctx = chartRef.value.getContext('2d')
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'top', labels: { font: { size: 11 }, usePointStyle: true, pointStyle: 'circle' } },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.y} kg` } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
        y: { beginAtZero: false, grid: { color: '#f3f4f6' }, ticks: { font: { size: 11 }, callback: (v) => v + ' kg' } },
      },
    },
  })
}

function openAddRecord() {
  editingRecord.value = null
  recordForm.value = { weight: null, date: new Date().toISOString().slice(0, 10), note: '' }
  showRecordModal.value = true
}

function openEditRecord(record) {
  editingRecord.value = record
  recordForm.value = {
    weight: record.weight,
    date: record.date,
    note: record.note || '',
  }
  showRecordModal.value = true
}

async function handleSubmitRecord() {
  if (!recordForm.value.weight || !store.activeProfileId) return
  if (editingRecord.value) {
    await store.updateRecord(editingRecord.value.id, {
      weight: recordForm.value.weight,
      note: recordForm.value.note || null,
    })
  } else {
    await store.createRecord(store.activeProfileId, {
      weight: recordForm.value.weight,
      date: recordForm.value.date,
      note: recordForm.value.note || null,
    })
  }
  showRecordModal.value = false
}

async function handleDeleteRecord(id) {
  if (confirm('确定删除此记录？')) {
    await store.deleteRecord(id)
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 sm:mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">体重记录</h1>
        <p class="text-xs sm:text-sm text-gray-500 mt-1">记录每日体重，关注健康变化</p>
      </div>
    </div>

    <!-- Profile tabs -->
    <div class="flex items-center gap-2 mb-4 sm:mb-5 flex-wrap">
      <div v-for="profile in store.profiles" :key="profile.id" class="flex items-center gap-1">
        <button
          @click="selectProfile(profile.id)"
          class="flex items-center gap-1 px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm rounded-xl font-medium transition-all duration-200 border"
          :class="profile.id === store.activeProfileId
            ? 'text-white shadow-md border-transparent'
            : 'text-gray-600 bg-white/60 hover:bg-white border-gray-200'"
          :style="profile.id === store.activeProfileId ? { background: profile.color || '#8b5cf6' } : {}"
        >
          {{ profile.name }}
          <span class="opacity-70 text-[10px]">({{ profile.record_count }})</span>
        </button>
        <button @click="openEditProfile(profile)" class="w-6 h-6 flex items-center justify-center rounded-md text-gray-300 hover:text-violet-500 hover:bg-violet-50 transition-colors" title="编辑角色">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z" /></svg>
        </button>
      </div>
      <button
        @click="openCreateProfile"
        class="px-3 py-1.5 text-xs sm:text-sm rounded-xl font-medium text-violet-600 bg-violet-50 hover:bg-violet-100 border border-violet-200 transition-all duration-200"
      >
        + 新建角色
      </button>
      <button
        v-if="activeProfile"
        @click="handleDeleteProfile(activeProfile.id)"
        class="px-2 py-1.5 text-xs rounded-xl text-gray-400 hover:text-rose-500 hover:bg-rose-50 transition-all duration-200"
        title="删除角色"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="text-center py-12 sm:py-16">
      <div class="inline-block w-8 h-8 sm:w-10 sm:h-10 border-3 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>
      <p class="text-gray-500 mt-3 sm:mt-4 text-sm">加载中...</p>
    </div>

    <!-- No profiles -->
    <div v-else-if="store.profiles.length === 0" class="text-center py-12 sm:py-20 bg-white/50 backdrop-blur-sm rounded-2xl sm:rounded-3xl border border-white/80 shadow-lg">
      <div class="text-5xl sm:text-6xl mb-4">⚖️</div>
      <p class="text-gray-600 text-base sm:text-lg font-medium mb-2">还没有角色</p>
      <p class="text-gray-400 text-xs sm:text-sm mb-4">创建一个角色开始记录体重吧~</p>
      <button
        @click="openCreateProfile"
        class="px-4 sm:px-5 py-2 sm:py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-xl hover:from-violet-700 hover:to-fuchsia-700 transition-all duration-300 shadow-lg shadow-violet-500/25 text-xs sm:text-sm font-medium"
      >
        + 新建角色
      </button>
    </div>

    <!-- Content -->
    <div v-else-if="activeProfile">
      <!-- Quick record -->
      <div class="bg-white/60 backdrop-blur-sm rounded-xl p-4 shadow-sm border border-white/80 mb-4">
        <div class="flex items-center gap-3">
          <div class="flex-1 relative">
            <input v-model.number="quickWeight" type="number" step="0.1" placeholder="今日体重 (kg)" class="w-full px-4 py-2.5 pr-8 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm" @keydown.enter="handleQuickRecord" />
            <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">kg</span>
          </div>
          <button @click="handleQuickRecord" :disabled="!quickWeight" class="px-5 py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-xl text-sm font-medium shadow-md shadow-violet-500/20 disabled:opacity-40 transition-all">记录</button>
        </div>
      </div>

      <!-- Stats -->
      <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <div class="bg-white/60 backdrop-blur-sm rounded-xl p-3 sm:p-4 shadow-sm border border-white/80">
          <div class="text-xs text-gray-400 mb-1">当前体重</div>
          <div class="text-lg sm:text-xl font-bold text-gray-800">{{ stats.current }} <span class="text-xs text-gray-400 font-normal">kg</span></div>
        </div>
        <div class="bg-white/60 backdrop-blur-sm rounded-xl p-3 sm:p-4 shadow-sm border border-white/80">
          <div class="text-xs text-gray-400 mb-1">较上次</div>
          <div class="text-lg sm:text-xl font-bold" :class="stats.change > 0 ? 'text-rose-500' : stats.change < 0 ? 'text-emerald-500' : 'text-gray-800'">
            {{ stats.change > 0 ? '+' : '' }}{{ stats.change }} <span class="text-xs text-gray-400 font-normal">kg</span>
          </div>
        </div>
        <div class="bg-white/60 backdrop-blur-sm rounded-xl p-3 sm:p-4 shadow-sm border border-white/80">
          <div class="text-xs text-gray-400 mb-1">最低 / 最高</div>
          <div class="text-lg sm:text-xl font-bold text-gray-800">{{ stats.min }} / {{ stats.max }} <span class="text-xs text-gray-400 font-normal">kg</span></div>
        </div>
        <div class="bg-white/60 backdrop-blur-sm rounded-xl p-3 sm:p-4 shadow-sm border border-white/80">
          <div class="text-xs text-gray-400 mb-1">{{ stats.bmi ? 'BMI' : '记录天数' }}</div>
          <div v-if="stats.bmi" class="text-lg sm:text-xl font-bold">
            {{ stats.bmi }}
            <span class="text-xs font-normal ml-1" :class="{ 'text-blue-500': stats.bmiCategory==='偏瘦', 'text-emerald-500': stats.bmiCategory==='正常', 'text-orange-500': stats.bmiCategory==='偏胖', 'text-rose-500': stats.bmiCategory==='肥胖' }">{{ stats.bmiCategory }}</span>
          </div>
          <div v-else class="text-lg sm:text-xl font-bold text-gray-800">{{ stats.days }} <span class="text-xs text-gray-400 font-normal">天</span></div>
        </div>
      </div>

      <!-- Target progress -->
      <div v-if="stats?.targetProgress !== null" class="bg-white/60 backdrop-blur-sm rounded-xl p-4 shadow-sm border border-white/80 mb-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs text-gray-500">目标体重: {{ stats.targetWeight }} kg</span>
          <span class="text-xs font-medium text-violet-600">{{ stats.targetProgress }}%</span>
        </div>
        <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500 transition-all duration-500" :style="{ width: stats.targetProgress + '%' }"></div>
        </div>
        <div class="text-xs text-gray-400 mt-1.5">距目标还差 {{ Math.abs(stats.current - stats.targetWeight).toFixed(1) }} kg</div>
      </div>

      <!-- Chart -->
      <div class="bg-white/60 backdrop-blur-sm rounded-xl sm:rounded-2xl p-3 sm:p-5 shadow-sm border border-white/80 mb-4 sm:mb-5">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm sm:text-base font-bold text-gray-700">体重趋势</h3>
          <button @click="toggleCompare" class="px-2 py-1 text-[10px] sm:text-xs rounded-lg transition-all" :class="compareMode ? 'bg-violet-100 text-violet-700 font-medium' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'">对比</button>
        </div>
        <div v-if="compareMode" class="flex gap-2 mb-3 flex-wrap">
          <button v-for="p in store.profiles" :key="p.id" @click="toggleCompareProfile(p.id)" class="px-2 py-1 text-[10px] rounded-lg border transition-all" :class="compareSet.has(p.id) ? 'text-white border-transparent' : 'text-gray-500 border-gray-200 bg-white'" :style="compareSet.has(p.id) ? { background: p.color } : {}">{{ p.name }}</button>
        </div>
        <div class="flex gap-1 mb-3">
          <button v-for="opt in rangeOptions" :key="opt.value" @click="timeRange = opt.value" class="px-2 py-1 text-[10px] sm:text-xs rounded-lg transition-all" :class="timeRange === opt.value ? 'bg-violet-100 text-violet-700 font-medium' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'">{{ opt.label }}</button>
        </div>
        <div class="relative" style="height: 220px">
          <canvas ref="chartRef"></canvas>
          <div v-if="store.records.length === 0" class="absolute inset-0 flex items-center justify-center bg-white/40 rounded-lg">
            <p class="text-gray-400 text-sm">暂无数据，添加记录后显示图表</p>
          </div>
        </div>
      </div>

      <!-- Records -->
      <div class="bg-white/60 backdrop-blur-sm rounded-xl sm:rounded-2xl shadow-sm border border-white/80 overflow-hidden">
        <div class="flex items-center justify-between px-3 sm:px-5 py-3 sm:py-4 border-b border-gray-100">
          <h3 class="text-sm sm:text-base font-bold text-gray-700">记录列表</h3>
          <button
            @click="openAddRecord"
            class="px-3 sm:px-4 py-1.5 text-xs sm:text-sm bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-lg hover:from-violet-700 hover:to-fuchsia-700 transition-all duration-200 font-medium shadow-md shadow-violet-500/20"
          >
            + 添加记录
          </button>
        </div>

        <div v-if="store.records.length === 0" class="text-center py-8">
          <p class="text-gray-400 text-sm">还没有记录</p>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div
            v-for="record in store.records"
            :key="record.id"
            class="flex items-center justify-between px-3 sm:px-5 py-3 sm:py-3.5 hover:bg-white/50 transition-colors duration-200 group"
          >
            <div class="flex items-center gap-3 sm:gap-4">
              <span class="text-xs sm:text-sm text-gray-500 w-12 sm:w-14">{{ formatDate(record.date) }}</span>
              <span class="text-sm sm:text-base font-bold text-gray-800">{{ record.weight }} <span class="text-xs text-gray-400 font-normal">kg</span></span>
              <span v-if="record.note" class="text-[10px] sm:text-xs text-gray-400 hidden sm:inline">{{ record.note }}</span>
            </div>
            <div class="flex items-center gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-200">
              <button
                @click="openEditRecord(record)"
                class="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-violet-600 hover:bg-violet-50 transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>
              </button>
              <button
                @click="handleDeleteRecord(record.id)"
                class="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Modal (Create + Edit) -->
    <div v-if="showProfileModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4" @click.self="showProfileModal = false">
      <div class="bg-white rounded-2xl shadow-2xl p-5 sm:p-6 w-full max-w-sm border border-white/80" @click.stop>
        <h3 class="text-base sm:text-lg font-bold text-gray-800 mb-4">{{ editingProfile ? '编辑角色' : '新建角色' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-1">角色名称</label>
            <input v-model="profileForm.name" placeholder="如：我自己、妈妈" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent transition-all" />
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-2">颜色</label>
            <div class="flex gap-2 flex-wrap">
              <button v-for="c in colorOptions" :key="c.value" @click="profileForm.color = c.value" class="w-8 h-8 rounded-full border-2 transition-all duration-200" :class="profileForm.color === c.value ? 'border-gray-800 scale-110 shadow-md' : 'border-transparent'" :style="{ background: c.value }"></button>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-1">身高 (cm)</label>
              <input v-model.number="profileForm.height" type="number" step="0.1" placeholder="170" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-400" />
              <p class="text-[10px] text-gray-400 mt-0.5">设置后自动计算 BMI</p>
            </div>
            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-1">目标体重 (kg)</label>
              <input v-model.number="profileForm.target_weight" type="number" step="0.1" placeholder="60.0" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-400" />
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button @click="showProfileModal = false" class="px-4 py-2 text-xs sm:text-sm text-gray-500 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all">取消</button>
          <button @click="handleSaveProfile" class="px-4 py-2 text-xs sm:text-sm text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl hover:from-violet-700 hover:to-fuchsia-700 transition-all shadow-md shadow-violet-500/20">{{ editingProfile ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Record Modal -->
    <div v-if="showRecordModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4" @click.self="showRecordModal = false">
      <div class="bg-white rounded-2xl shadow-2xl p-5 sm:p-6 w-full max-w-sm border border-white/80" @click.stop>
        <h3 class="text-base sm:text-lg font-bold text-gray-800 mb-4">{{ editingRecord ? '编辑记录' : '添加记录' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-1">日期</label>
            <input
              v-model="recordForm.date"
              type="date"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent transition-all"
            />
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-1">体重 (kg)</label>
            <input
              v-model.number="recordForm.weight"
              type="number"
              step="0.1"
              placeholder="65.0"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent transition-all"
            />
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-1">备注（可选）</label>
            <input
              v-model="recordForm.note"
              placeholder="如：早餐前"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent transition-all"
            />
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button @click="showRecordModal = false" class="px-4 py-2 text-xs sm:text-sm text-gray-500 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all">取消</button>
          <button @click="handleSubmitRecord" class="px-4 py-2 text-xs sm:text-sm text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl hover:from-violet-700 hover:to-fuchsia-700 transition-all shadow-md shadow-violet-500/20">
            {{ editingRecord ? '保存' : '添加' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>