import { defineStore } from 'pinia'
import { ref } from 'vue'
import { weightsApi } from '../api/weights'

export const useWeightStore = defineStore('weight', () => {
  const profiles = ref([])
  const records = ref([])
  const activeProfileId = ref(null)
  const loading = ref(false)

  async function fetchProfiles() {
    loading.value = true
    try {
      const { data } = await weightsApi.listProfiles()
      profiles.value = data
      if (data.length && !activeProfileId.value) {
        activeProfileId.value = data[0].id
      }
    } finally {
      loading.value = false
    }
  }

  async function createProfile(profileData) {
    const { data } = await weightsApi.createProfile(profileData)
    profiles.value.push(data)
    if (!activeProfileId.value) {
      activeProfileId.value = data.id
    }
    return data
  }

  async function deleteProfile(id) {
    await weightsApi.deleteProfile(id)
    profiles.value = profiles.value.filter(p => p.id !== id)
    if (activeProfileId.value === id) {
      activeProfileId.value = profiles.value[0]?.id || null
      if (activeProfileId.value) await fetchRecords(activeProfileId.value)
      else records.value = []
    }
  }

  async function fetchRecords(profileId) {
    const { data } = await weightsApi.listRecords(profileId)
    records.value = data
  }

  async function createRecord(profileId, recordData) {
    const { data } = await weightsApi.createRecord(profileId, recordData)
    records.value.unshift(data)
    // Refresh profile list to update record_count
    await fetchProfiles()
    return data
  }

  async function updateRecord(id, recordData) {
    const { data } = await weightsApi.updateRecord(id, recordData)
    const idx = records.value.findIndex(r => r.id === id)
    if (idx !== -1) records.value[idx] = data
    return data
  }

  async function deleteRecord(id) {
    await weightsApi.deleteRecord(id)
    records.value = records.value.filter(r => r.id !== id)
    await fetchProfiles()
  }

  function setActiveProfile(id) {
    activeProfileId.value = id
    if (id) fetchRecords(id)
  }

  return {
    profiles, records, activeProfileId, loading,
    fetchProfiles, createProfile, deleteProfile,
    fetchRecords, createRecord, updateRecord, deleteRecord,
    setActiveProfile,
  }
})