<script setup>
import { onMounted } from 'vue'
import { useScheduleStore } from '../stores/schedule'

const store = useScheduleStore()

onMounted(() => {
  store.fetchSchedules()
})

const priorityLabels = { 0: '普通', 1: '重要', 2: '紧急' }
const statusLabels = { pending: '待办', in_progress: '进行中', completed: '已完成' }
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">日程管理</h1>
      <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        + 新建日程
      </button>
    </div>

    <div v-if="store.loading" class="text-center py-8 text-gray-500">加载中...</div>

    <div v-else-if="store.schedules.length === 0" class="text-center py-12 text-gray-400">
      暂无日程，点击上方按钮创建
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="schedule in store.schedules"
        :key="schedule.id"
        class="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold">{{ schedule.title }}</h3>
          <div class="flex items-center gap-2">
            <span
              class="px-2 py-1 text-xs rounded"
              :class="{
                'bg-gray-100 text-gray-600': schedule.priority === 0,
                'bg-yellow-100 text-yellow-700': schedule.priority === 1,
                'bg-red-100 text-red-700': schedule.priority === 2,
              }"
            >
              {{ priorityLabels[schedule.priority] }}
            </span>
            <span
              class="px-2 py-1 text-xs rounded"
              :class="{
                'bg-blue-100 text-blue-700': schedule.status === 'pending',
                'bg-orange-100 text-orange-700': schedule.status === 'in_progress',
                'bg-green-100 text-green-700': schedule.status === 'completed',
              }"
            >
              {{ statusLabels[schedule.status] }}
            </span>
          </div>
        </div>
        <p v-if="schedule.description" class="text-gray-600 mt-2">{{ schedule.description }}</p>
        <p class="text-sm text-gray-400 mt-2">
          {{ new Date(schedule.start_time).toLocaleString() }}
        </p>
      </div>
    </div>
  </div>
</template>
