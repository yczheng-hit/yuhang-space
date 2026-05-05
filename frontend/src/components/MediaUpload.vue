<script setup>
import { ref } from 'vue'

const props = defineProps({
  uploadFn: { type: Function, required: true },
  existingMedia: { type: Array, default: () => [] },
})

const emit = defineEmits(['uploaded', 'delete-media'])

const fileInput = ref(null)
const previews = ref([])
const uploading = ref(false)
const error = ref('')

function openPicker() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const files = Array.from(e.target.files)
  for (const file of files) {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (ev) => {
        previews.value.push({ file, url: ev.target.result, type: 'image' })
      }
      reader.readAsDataURL(file)
    } else if (file.type.startsWith('video/')) {
      previews.value.push({ file, url: URL.createObjectURL(file), type: 'video' })
    }
  }
  e.target.value = ''
}

function removePreview(index) {
  previews.value.splice(index, 1)
}

async function uploadAll() {
  if (previews.value.length === 0) return
  uploading.value = true
  error.value = ''
  try {
    for (const item of previews.value) {
      await props.uploadFn(item.file)
    }
    previews.value = []
    emit('uploaded')
  } catch (e) {
    error.value = e.response?.data?.detail || '上传失败'
  } finally {
    uploading.value = false
  }
}

function getMediaUrl(filePath) {
  const base = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'
  return `${base}/media/${filePath}`
}
</script>

<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">图片 / 视频</label>

    <!-- 已有媒体 -->
    <div v-if="existingMedia.length" class="flex gap-2 flex-wrap mb-3">
      <div
        v-for="media in existingMedia"
        :key="media.id"
        class="relative w-20 h-20 rounded overflow-hidden border border-gray-200 group"
      >
        <img
          v-if="media.file_type === 'image'"
          :src="getMediaUrl(media.file_path)"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full bg-gray-100 flex items-center justify-center">
          <span class="text-2xl">🎬</span>
        </div>
        <button
          type="button"
          @click="emit('delete-media', media.id)"
          class="absolute top-0 right-0 w-5 h-5 bg-black/60 text-white text-xs flex items-center justify-center rounded-bl opacity-0 group-hover:opacity-100 transition-opacity"
        >&times;</button>
      </div>
    </div>

    <!-- 待上传预览 -->
    <div v-if="previews.length" class="flex gap-2 flex-wrap mb-3">
      <div
        v-for="(item, index) in previews"
        :key="index"
        class="relative w-20 h-20 rounded overflow-hidden border border-blue-300"
      >
        <img v-if="item.type === 'image'" :src="item.url" class="w-full h-full object-cover" />
        <video v-else :src="item.url" class="w-full h-full object-cover" muted />
        <button
          type="button"
          @click="removePreview(index)"
          class="absolute top-0 right-0 w-5 h-5 bg-black/60 text-white text-xs flex items-center justify-center rounded-bl"
        >&times;</button>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <button
        type="button"
        @click="openPicker"
        class="px-3 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 text-sm"
      >
        选择文件
      </button>
      <button
        v-if="previews.length"
        type="button"
        @click="uploadAll"
        :disabled="uploading"
        class="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm disabled:opacity-50"
      >
        {{ uploading ? '上传中...' : `上传 (${previews.length})` }}
      </button>
      <span class="text-xs text-gray-400">支持 jpg/png/gif/webp/mp4/mov，最大 50MB</span>
    </div>
    <p v-if="error" class="text-sm text-red-500 mt-1">{{ error }}</p>

    <input
      ref="fileInput"
      type="file"
      accept="image/*,video/*"
      multiple
      class="hidden"
      @change="onFileChange"
    />
  </div>
</template>
