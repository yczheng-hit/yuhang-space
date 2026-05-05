<script setup>
import { ref, onMounted } from 'vue'
import { schedulesApi } from '../api/schedules'
import MediaUpload from './MediaUpload.vue'

const props = defineProps({
  entry: { type: Object, default: null },
})

const emit = defineEmits(['close', 'submit'])

const isEdit = !!props.entry

const form = ref({
  title: props.entry?.title || '',
  description: props.entry?.description || '',
  start_time: props.entry?.start_time
    ? new Date(props.entry.start_time).toISOString().slice(0, 16)
    : new Date().toISOString().slice(0, 16),
  priority: props.entry?.priority ?? 1,
  tags: props.entry?.tags ? [...props.entry.tags] : [],
})

const tagInput = ref('')
const submitting = ref(false)
const mediaList = ref([])

const moods = [
  { value: 0, emoji: '😊', label: '开心' },
  { value: 1, emoji: '😐', label: '平静' },
  { value: 2, emoji: '😢', label: '难过' },
  { value: 3, emoji: '😡', label: '生气' },
  { value: 4, emoji: '🤔', label: '纠结' },
]

onMounted(async () => {
  if (props.entry) {
    try {
      const { data } = await schedulesApi.listMedia(props.entry.id)
      mediaList.value = data
    } catch {}
  }
})

function addTag() {
  const tag = tagInput.value.trim()
  if (tag && !form.value.tags.includes(tag)) {
    form.value.tags.push(tag)
  }
  tagInput.value = ''
}

function removeTag(index) {
  form.value.tags.splice(index, 1)
}

async function handleUpload(file) {
  await schedulesApi.uploadMedia(props.entry.id, file)
  const { data } = await schedulesApi.listMedia(props.entry.id)
  mediaList.value = data
}

async function handleDeleteMedia(mediaId) {
  await schedulesApi.deleteMedia(props.entry.id, mediaId)
  mediaList.value = mediaList.value.filter(m => m.id !== mediaId)
}

async function handleSubmit() {
  if (!form.value.title.trim()) return
  submitting.value = true
  try {
    await emit('submit', {
      ...form.value,
      start_time: new Date(form.value.start_time).toISOString(),
    })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold">{{ isEdit ? '编辑日记' : '写日记' }}</h2>
          <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
            <input
              v-model="form.title"
              type="text"
              required
              placeholder="今天发生了什么..."
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">内容</label>
            <textarea
              v-model="form.description"
              rows="5"
              placeholder="记录一下今天的心情和故事..."
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">日期</label>
            <input
              v-model="form.start_time"
              type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">今天的心情</label>
            <div class="flex gap-3">
              <button
                v-for="mood in moods"
                :key="mood.value"
                type="button"
                @click="form.priority = mood.value"
                class="flex flex-col items-center p-2 rounded-lg border-2 transition-all"
                :class="form.priority === mood.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'"
              >
                <span class="text-2xl">{{ mood.emoji }}</span>
                <span class="text-xs text-gray-500 mt-1">{{ mood.label }}</span>
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标签</label>
            <div class="flex gap-2 mb-2 flex-wrap">
              <span
                v-for="(tag, index) in form.tags"
                :key="tag"
                class="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded flex items-center gap-1"
              >
                {{ tag }}
                <button type="button" @click="removeTag(index)" class="hover:text-blue-900">&times;</button>
              </span>
            </div>
            <div class="flex gap-2">
              <input
                v-model="tagInput"
                type="text"
                placeholder="输入标签后回车"
                @keydown.enter.prevent="addTag"
                class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                @click="addTag"
                class="px-3 py-2 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
              >
                添加
              </button>
            </div>
          </div>

          <!-- 媒体上传（仅编辑模式） -->
          <MediaUpload
            v-if="isEdit"
            :upload-fn="handleUpload"
            :existing-media="mediaList"
            @uploaded="() => {}"
            @delete-media="handleDeleteMedia"
          />

          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="emit('close')"
              class="flex-1 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="submitting || !form.title.trim()"
              class="flex-1 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {{ submitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
