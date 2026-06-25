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
    ? props.entry.start_time.slice(0, 16)
    : new Date().toLocaleString('sv-SE', { hour12: false }).slice(0, 16),
  priority: props.entry?.priority ?? 1,
  tags: props.entry?.tags ? [...props.entry.tags] : [],
})

const tagInput = ref('')
const submitting = ref(false)
const mediaList = ref([])
const mediaUploadRef = ref(null)
const pendingFiles = ref([])

const moods = [
  { value: 0, emoji: '😊', label: '开心', color: 'border-amber-400 bg-amber-50 shadow-amber-500/20' },
  { value: 1, emoji: '😌', label: '平静', color: 'border-sky-400 bg-sky-50 shadow-sky-500/20' },
  { value: 2, emoji: '😢', label: '难过', color: 'border-slate-400 bg-slate-50 shadow-slate-500/20' },
  { value: 3, emoji: '😤', label: '生气', color: 'border-rose-400 bg-rose-50 shadow-rose-500/20' },
  { value: 4, emoji: '🤔', label: '纠结', color: 'border-purple-400 bg-purple-50 shadow-purple-500/20' },
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

function onFilesChanged(files) {
  pendingFiles.value = files.map(f => f.file)
}

async function handleSubmit() {
  if (!form.value.title.trim()) return
  submitting.value = true
  try {
    const formData = {
      ...form.value,
      start_time: form.value.start_time.length === 16
        ? form.value.start_time + ':00'
        : form.value.start_time,
    }
    const created = await new Promise((resolve) => {
      emit('submit', formData, resolve)
    })

    if (!isEdit && created?.id && pendingFiles.value.length > 0) {
      for (const file of pendingFiles.value) {
        await schedulesApi.uploadMedia(created.id, file)
      }
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 backdrop-blur-md flex items-end sm:items-center justify-center z-50 animate-fade-in" @click.self="emit('close')">
    <div class="bg-white/95 sm:bg-white/90 backdrop-blur-xl w-full sm:max-w-lg sm:rounded-3xl rounded-t-3xl shadow-2xl shadow-violet-500/10 max-h-[92vh] sm:max-h-[90vh] overflow-y-auto animate-slide-up sm:animate-scale-in border border-white/80">
      <div class="p-5 sm:p-7">
        <!-- Drag handle on mobile -->
        <div class="flex justify-center mb-3 sm:hidden">
          <div class="w-10 h-1 bg-gray-300 rounded-full"></div>
        </div>

        <div class="flex items-center justify-between mb-5 sm:mb-7">
          <h2 class="text-lg sm:text-xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
            {{ isEdit ? '编辑日记' : '写日记' }} ✨
          </h2>
          <button @click="emit('close')" class="w-8 h-8 flex items-center justify-center rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all duration-200 text-xl">&times;</button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4 sm:space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">标题</label>
            <input
              v-model="form.title"
              type="text"
              required
              placeholder="今天发生了什么..."
              class="w-full px-4 py-2.5 sm:py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-400 transition-all duration-300 bg-white/50 focus:bg-white shadow-sm text-sm sm:text-base"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">内容</label>
            <textarea
              v-model="form.description"
              rows="3"
              placeholder="记录一下今天的心情和故事..."
              class="w-full px-4 py-2.5 sm:py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-400 transition-all duration-300 bg-white/50 focus:bg-white shadow-sm resize-none text-sm sm:text-base"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">日期</label>
            <input
              v-model="form.start_time"
              type="datetime-local"
              class="w-full px-4 py-2.5 sm:py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-400 transition-all duration-300 bg-white/50 focus:bg-white shadow-sm text-sm sm:text-base"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">今天的心情</label>
            <div class="flex gap-1.5 sm:gap-2 flex-wrap">
              <button
                v-for="mood in moods"
                :key="mood.value"
                type="button"
                @click="form.priority = mood.value"
                class="flex flex-col items-center p-2 sm:p-2.5 rounded-xl border-2 transition-all duration-300 min-w-[52px] sm:min-w-[60px]"
                :class="form.priority === mood.value
                  ? mood.color + ' shadow-md scale-105'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
              >
                <span class="text-xl sm:text-2xl">{{ mood.emoji }}</span>
                <span class="text-[10px] sm:text-xs text-gray-500 mt-0.5 sm:mt-1">{{ mood.label }}</span>
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5 sm:mb-2">标签</label>
            <div class="flex gap-1.5 sm:gap-2 mb-2 flex-wrap">
              <span
                v-for="(tag, index) in form.tags"
                :key="tag"
                class="px-2.5 sm:px-3 py-1 text-xs bg-gradient-to-r from-violet-50 to-fuchsia-50 text-violet-700 rounded-full flex items-center gap-1 border border-violet-100"
              >
                {{ tag }}
                <button type="button" @click="removeTag(index)" class="hover:text-rose-600 transition-colors">&times;</button>
              </span>
            </div>
            <div class="flex gap-2">
              <input
                v-model="tagInput"
                type="text"
                placeholder="输入标签后回车"
                @keydown.enter.prevent="addTag"
                class="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-400 transition-all duration-300 bg-white/50 focus:bg-white shadow-sm text-sm"
              />
              <button
                type="button"
                @click="addTag"
                class="px-3 sm:px-4 py-2.5 bg-gradient-to-r from-violet-50 to-fuchsia-50 text-violet-600 rounded-xl hover:from-violet-100 hover:to-fuchsia-100 transition-all duration-200 text-sm border border-violet-100 flex-shrink-0"
              >
                添加
              </button>
            </div>
          </div>

          <!-- Media upload -->
          <MediaUpload
            ref="mediaUploadRef"
            :upload-fn="isEdit ? handleUpload : null"
            :existing-media="mediaList"
            @uploaded="() => {}"
            @delete-media="handleDeleteMedia"
            @files-changed="onFilesChanged"
          />

          <div class="flex gap-3 pt-2 pb-1 sm:pb-0">
            <button
              type="button"
              @click="emit('close')"
              class="flex-1 py-2.5 sm:py-3 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition-all duration-200 font-medium text-sm sm:text-base"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="submitting || !form.title.trim()"
              class="flex-1 py-2.5 sm:py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-xl hover:from-violet-700 hover:to-fuchsia-700 disabled:opacity-50 transition-all duration-300 font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 text-sm sm:text-base"
            >
              {{ submitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slide-up {
  from { opacity: 0; transform: translateY(100%); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.animate-fade-in { animation: fade-in 0.25s ease-out; }
.animate-slide-up { animation: slide-up 0.35s cubic-bezier(0.16, 1, 0.3, 1); }
.animate-scale-in { animation: scale-in 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
</style>
