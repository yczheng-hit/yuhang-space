import api from './index'

export const recipesApi = {
  list(params = {}) {
    return api.get('/recipes', { params })
  },

  get(id) {
    return api.get(`/recipes/${id}`)
  },

  create(data) {
    return api.post('/recipes', data)
  },

  update(id, data) {
    return api.patch(`/recipes/${id}`, data)
  },

  delete(id) {
    return api.delete(`/recipes/${id}`)
  },

  uploadMedia(id, file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/recipes/${id}/media`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  listMedia(id) {
    return api.get(`/recipes/${id}/media`)
  },
}
