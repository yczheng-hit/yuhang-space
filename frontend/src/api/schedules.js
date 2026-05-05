import api from './index'

export const schedulesApi = {
  list(params = {}) {
    return api.get('/schedules', { params })
  },

  get(id) {
    return api.get(`/schedules/${id}`)
  },

  create(data) {
    return api.post('/schedules', data)
  },

  update(id, data) {
    return api.patch(`/schedules/${id}`, data)
  },

  delete(id) {
    return api.delete(`/schedules/${id}`)
  },

  uploadMedia(id, file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/schedules/${id}/media`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  listMedia(id) {
    return api.get(`/schedules/${id}/media`)
  },

  deleteMedia(scheduleId, mediaId) {
    return api.delete(`/schedules/${scheduleId}/media/${mediaId}`)
  },
}
