import api from './index'

export const authApi = {
  register(data) {
    return api.post('/auth/register', data)
  },

  login(data) {
    return api.post('/auth/login', data)
  },

  refresh(refreshToken) {
    return api.post('/auth/refresh', { refresh_token: refreshToken })
  },
}
