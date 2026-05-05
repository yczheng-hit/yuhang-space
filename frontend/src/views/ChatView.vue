<script setup>
import { ref } from 'vue'
import { llmApi } from '../api/llm'

const messages = ref([])
const input = ref('')
const loading = ref(false)

async function sendMessage() {
  if (!input.value.trim() || loading.value) return

  const userMessage = input.value.trim()
  messages.value.push({ role: 'user', content: userMessage })
  input.value = ''
  loading.value = true

  try {
    const response = await llmApi.chat(userMessage)
    const reader = response.data.getReader()
    const decoder = new TextDecoder()
    let assistantMessage = ''

    messages.value.push({ role: 'assistant', content: '' })

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') break
          try {
            const parsed = JSON.parse(data)
            assistantMessage += parsed.content
            messages.value[messages.value.length - 1].content = assistantMessage
          } catch {}
        }
      }
    }
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，AI 服务暂时不可用。请检查 LLM 配置。',
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">AI 助手</h1>

    <div class="bg-white rounded-lg shadow h-[60vh] flex flex-col">
      <!-- 消息列表 -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <div v-if="messages.length === 0" class="text-center text-gray-400 py-12">
          开始和 AI 助手对话吧！可以让她帮你创建日程或推荐菜谱。
        </div>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="msg.role === 'user' ? 'text-right' : 'text-left'"
        >
          <div
            class="inline-block max-w-[80%] px-4 py-2 rounded-lg"
            :class="
              msg.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-800'
            "
          >
            {{ msg.content }}
          </div>
        </div>

        <div v-if="loading" class="text-left">
          <div class="inline-block px-4 py-2 bg-gray-100 rounded-lg text-gray-500">
            思考中...
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <form @submit.prevent="sendMessage" class="border-t p-4 flex gap-2">
        <input
          v-model="input"
          type="text"
          placeholder="输入消息..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          :disabled="loading || !input.trim()"
          class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          发送
        </button>
      </form>
    </div>
  </div>
</template>
