import api from './index'

export const weightsApi = {
  listProfiles() {
    return api.get('/weights/profiles')
  },
  createProfile(data) {
    return api.post('/weights/profiles', data)
  },
  updateProfile(id, data) {
    return api.patch(`/weights/profiles/${id}`, data)
  },
  deleteProfile(id) {
    return api.delete(`/weights/profiles/${id}`)
  },
  listRecords(profileId, params = {}) {
    return api.get(`/weights/profiles/${profileId}/records`, { params })
  },
  createRecord(profileId, data) {
    return api.post(`/weights/profiles/${profileId}/records`, data)
  },
  updateRecord(id, data) {
    return api.patch(`/weights/records/${id}`, data)
  },
  deleteRecord(id) {
    return api.delete(`/weights/records/${id}`)
  },
}