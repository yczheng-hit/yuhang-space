import api from './index'

export const llmApi = {
  chat(message) {
    return api.post('/llm/chat', { message }, { responseType: 'stream' })
  },

  generateSchedule(prompt) {
    return api.post('/llm/generate-schedule', { prompt })
  },

  generateRecipe(prompt) {
    return api.post('/llm/generate-recipe', { prompt })
  },
}
