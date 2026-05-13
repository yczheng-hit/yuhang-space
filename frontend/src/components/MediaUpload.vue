<script setup>
import { ref } from 'vue'

const props = defineProps({
  uploadFn: { type: Function, default: null },
  existingMedia: { type: Array, default: () => [] },
})

const emit = defineEmits(['uploaded', 'delete-media', 'files-changed'])

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
        previews.value.push({ file, url: ev.target.result, type: 'image', mediaType: 'cover' })
        emit('files-changed', previews.value)
      }
      reader.readAsDataURL(file)
    } else if (file.type.startsWith('video/')) {
      previews.value.push({ file, url: URL.createObjectURL(file), type: 'video', mediaType: 'step' })
      emit('files-changed', previews.value)
    }
  }
  e.target.value = ''
}

function removePreview(index) {
  previews.value.splice(index, 1)
  emit('files-changed', previews.value)
}

function clearPreviews() {
  previews.value = []
}

async function uploadAll() {
  if (!props.uploadFn || previews.value.length === 0) return
  uploading.value = true
  error.value = ''
  try {
    for (const item of previews.value) {
      await props.uploadFn(item.file, item.mediaType)
    }
    previews.value = []
    emit('uploaded')
  } catch (e) {
    error.value = e.response?.data?.detail || '上传失败'
  } finally {
    uploading.value = false
  }
}

defineExpose({ uploadAll, clearPreviews, uploading })

function getMediaUrl(filePath) {
  return `/media/${filePath}`
}

function getMediaTypeLabel(type) {
  return type === 'cover' ? '成品图' : '步骤图'
}
</script>

<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">图片 / 视频</label>

    <!-- 已有媒体（编辑模式） -->
    <div v-if="existingMedia.length" class="flex gap-2 flex-wrap mb-3">
      <div
        v-for="media in existingMedia"
        :key="media.id"
        class="relative w-20 h-20 rounded-lg overflow-hidden border border-gray-200 group"
      >
        <img
          v-if="media.file_type === 'image'"
          :src="getMediaUrl(media.file_path)"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full bg-gray-900 flex items-center justify-center">
          <span class="text-white text-lg">▶</span>
        </div>
        <span
          v-if="media.media_type"
          class="absolute bottom-0 left-0 right-0 text-xs text-white bg-black/60 text-center py-0.5"
        >{{ getMediaTypeLabel(media.media_type) }}</span>
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
        class="relative w-20 h-20 rounded-lg overflow-hidden border-2 border-indigo-300"
      >
        <img v-if="item.type === 'image'" :src="item.url" class="w-full h-full object-cover" />
        <video v-else :src="item.url" class="w-full h-full object-cover" muted />
        <select
          v-model="item.mediaType"
          class="absolute bottom-0 left-0 right-0 text-xs bg-black/70 text-white border-none outline-none text-center py-0.5 cursor-pointer"
        >
          <option value="cover">成品图</option>
          <option value="step">步骤图</option>
        </select>
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
        class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 text-sm transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 inline mr-1 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" /></svg>
        选择文件
      </button>
      <button
        v-if="previews.length && uploadFn"
        type="button"
        @click="uploadAll"
        :disabled="uploading"
        class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm disabled:opacity-50 transition-colors"
      >
        {{ uploading ? '上传中...' : `上传 (${previews.length})` }}
      </button>
      <span v-if="previews.length && !uploadFn" class="text-xs text-indigo-500">
        {{ previews.length }} 个文件待上传（保存后自动上传）
      </span>
      <span v-else class="text-xs text-gray-400">支持 jpg/png/gif/webp/mp4/mov，最大 50MB</span>
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
