<script setup>
import { ref } from 'vue'

const props = defineProps({
  media: { type: Array, default: () => [] },
})

const lightbox = ref(null)

function openLightbox(item) {
  lightbox.value = item
}

function closeLightbox() {
  lightbox.value = null
}

function getMediaUrl(filePath) {
  const base = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'
  return `${base}/media/${filePath}`
}
</script>

<template>
  <div v-if="media.length">
    <div class="flex gap-2 flex-wrap">
      <div
        v-for="item in media"
        :key="item.id"
        class="w-24 h-24 rounded overflow-hidden cursor-pointer border border-gray-200 hover:border-blue-400 transition-colors"
        @click="openLightbox(item)"
      >
        <img
          v-if="item.file_type === 'image'"
          :src="getMediaUrl(item.file_path)"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full bg-gray-900 flex items-center justify-center relative">
          <video :src="getMediaUrl(item.file_path)" class="w-full h-full object-cover" muted />
          <span class="absolute inset-0 flex items-center justify-center text-white text-2xl bg-black/30">▶</span>
        </div>
      </div>
    </div>

    <!-- Lightbox -->
    <div
      v-if="lightbox"
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-[60] cursor-pointer"
      @click="closeLightbox"
    >
      <div class="max-w-[90vw] max-h-[90vh]" @click.stop>
        <img
          v-if="lightbox.file_type === 'image'"
          :src="getMediaUrl(lightbox.file_path)"
          class="max-w-full max-h-[90vh] object-contain rounded"
        />
        <video
          v-else
          :src="getMediaUrl(lightbox.file_path)"
          controls
          autoplay
          class="max-w-full max-h-[90vh] rounded"
        />
      </div>
      <button
        @click="closeLightbox"
        class="absolute top-4 right-4 text-white text-3xl hover:text-gray-300"
      >&times;</button>
    </div>
  </div>
</template>
