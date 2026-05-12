import api from './index'

export const llmApi = {
  chat(message) {
    return api.post('/llm/chat', { message }, { responseType: 'stream' })
  },

}
