import { defineStore } from 'pinia'
import { ref } from 'vue'
import { schedulesApi } from '../api/schedules'

export const useScheduleStore = defineStore('schedule', () => {
  const schedules = ref([])
  const loading = ref(false)

  async function fetchSchedules() {
    loading.value = true
    try {
      const { data } = await schedulesApi.list()
      schedules.value = data
    } finally {
      loading.value = false
    }
  }

  async function createSchedule(scheduleData) {
    const { data } = await schedulesApi.create(scheduleData)
    schedules.value.unshift(data)
    return data
  }

  async function updateSchedule(id, scheduleData) {
    const { data } = await schedulesApi.update(id, scheduleData)
    const index = schedules.value.findIndex((s) => s.id === id)
    if (index !== -1) schedules.value[index] = data
    return data
  }

  async function deleteSchedule(id) {
    await schedulesApi.delete(id)
    schedules.value = schedules.value.filter((s) => s.id !== id)
  }

  return { schedules, loading, fetchSchedules, createSchedule, updateSchedule, deleteSchedule }
})
