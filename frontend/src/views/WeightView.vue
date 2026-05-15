<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useWeightStore } from '../stores/weight'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const store = useWeightStore()
const showProfileModal = ref(false)
const showRecordModal = ref(false)
const editingRecord = ref(null)
const newProfileName = ref('')
const newProfileColor = ref('#8b5cf6')
const recordForm = ref({ weight: null, date: new Date().toISOString().slice(0, 10), note: '' })
const chartRef = ref(null)
let chartInstance = null

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

const chartData = computed(() => {
  const sorted = [...store.records].sort((a, b) => a.date.localeCompare(b.date))
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
  newProfileName.value = ''
  newProfileColor.value = '#8b5cf6'
  showProfileModal.value = true
}

async function handleCreateProfile() {
  if (!newProfileName.value.trim()) return
  await store.createProfile({
    name: newProfileName.value.trim(),
    color: newProfileColor.value,
  })
  showProfileModal.value = false
}

async function handleDeleteProfile(id) {
  if (confirm('确定删除此角色及其所有体重记录？')) {
    await store.deleteProfile(id)
  }
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
      <button
        v-for="profile in store.profiles"
        :key="profile.id"
        @click="selectProfile(profile.id)"
        class="px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm rounded-xl font-medium transition-all duration-200 border"
        :class="profile.id === store.activeProfileId
          ? 'text-white shadow-md border-transparent'
          : 'text-gray-600 bg-white/60 hover:bg-white border-gray-200'"
        :style="profile.id === store.activeProfileId ? { background: profile.color || '#8b5cf6' } : {}"
      >
        {{ profile.name }}
        <span class="ml-1.5 opacity-70 text-[10px]">({{ profile.record_count }})</span>
      </button>
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
      <!-- Chart -->
      <div class="bg-white/60 backdrop-blur-sm rounded-xl sm:rounded-2xl p-3 sm:p-5 shadow-sm border border-white/80 mb-4 sm:mb-5">
        <h3 class="text-sm sm:text-base font-bold text-gray-700 mb-3">体重趋势</h3>
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

    <!-- Create Profile Modal -->
    <div v-if="showProfileModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4" @click.self="showProfileModal = false">
      <div class="bg-white rounded-2xl shadow-2xl p-5 sm:p-6 w-full max-w-sm border border-white/80" @click.stop>
        <h3 class="text-base sm:text-lg font-bold text-gray-800 mb-4">新建角色</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-1">角色名称</label>
            <input
              v-model="newProfileName"
              placeholder="如：我自己、妈妈"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent transition-all"
            />
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-600 mb-2">颜色</label>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="c in colorOptions"
                :key="c.value"
                @click="newProfileColor = c.value"
                class="w-8 h-8 rounded-full border-2 transition-all duration-200"
                :class="newProfileColor === c.value ? 'border-gray-800 scale-110 shadow-md' : 'border-transparent'"
                :style="{ background: c.value }"
              ></button>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button @click="showProfileModal = false" class="px-4 py-2 text-xs sm:text-sm text-gray-500 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all">取消</button>
          <button @click="handleCreateProfile" class="px-4 py-2 text-xs sm:text-sm text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl hover:from-violet-700 hover:to-fuchsia-700 transition-all shadow-md shadow-violet-500/20">创建</button>
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