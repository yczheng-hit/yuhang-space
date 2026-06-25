<script setup>
import { ref, onMounted } from 'vue'
import { recipesApi } from '../api/recipes'
import MediaGallery from './MediaGallery.vue'

const props = defineProps({
  recipe: { type: Object, required: true },
})

const emit = defineEmits(['close', 'order'])

const mediaList = ref([])

onMounted(async () => {
  try {
    const { data } = await recipesApi.listMedia(props.recipe.id)
    mediaList.value = data
  } catch {}
})

function getCoverImage() {
  const cover = mediaList.value.find(m => m.media_type === 'cover' && m.file_type === 'image')
  return cover || mediaList.value.find(m => m.file_type === 'image') || null
}

function getMediaUrl(filePath) {
  return `/media/${filePath}`
}

function getStepImages() {
  return mediaList.value.filter(m => m.media_type === 'step' && m.file_type === 'image')
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 backdrop-blur-md flex items-end sm:items-center justify-center z-50 animate-fade-in" @click.self="emit('close')">
    <div class="bg-white w-full sm:max-w-lg sm:rounded-3xl rounded-t-3xl shadow-2xl max-h-[92vh] sm:max-h-[90vh] overflow-y-auto animate-slide-up sm:animate-scale-in">
      <!-- Drag handle mobile -->
      <div class="flex justify-center pt-3 sm:hidden">
        <div class="w-10 h-1 bg-gray-300 rounded-full"></div>
      </div>

      <!-- Header -->
      <div class="sticky top-0 bg-white/90 backdrop-blur-xl z-10 flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <h2 class="text-lg font-bold text-gray-800 pr-8 truncate">{{ recipe.title }}</h2>
        <button @click="emit('close')" class="w-8 h-8 flex items-center justify-center rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all text-xl">&times;</button>
      </div>

      <div class="p-5 space-y-5">
        <!-- Cover image -->
        <div v-if="getCoverImage()" class="rounded-2xl overflow-hidden">
          <img :src="getMediaUrl(getCoverImage().file_path)" class="w-full h-48 sm:h-56 object-cover" />
        </div>

        <!-- Description -->
        <p v-if="recipe.description" class="text-gray-600 text-sm leading-relaxed">{{ recipe.description }}</p>

        <!-- Meta info -->
        <div class="flex flex-wrap gap-3 text-sm text-gray-500">
          <span v-if="recipe.prep_time_min" class="flex items-center gap-1 bg-gray-50 px-3 py-1.5 rounded-lg">
            <span class="text-gray-400">准备</span> {{ recipe.prep_time_min }} 分钟
          </span>
          <span v-if="recipe.cook_time_min" class="flex items-center gap-1 bg-gray-50 px-3 py-1.5 rounded-lg">
            <span class="text-gray-400">烹饪</span> {{ recipe.cook_time_min }} 分钟
          </span>
          <span v-if="recipe.servings" class="flex items-center gap-1 bg-gray-50 px-3 py-1.5 rounded-lg">
            <span class="text-gray-400">份量</span> {{ recipe.servings }} 人份
          </span>
          <span v-if="recipe.price > 0" class="flex items-center gap-1 bg-orange-50 text-orange-600 px-3 py-1.5 rounded-lg font-bold">
            ¥{{ recipe.price.toFixed(2) }}
          </span>
        </div>

        <!-- Tags -->
        <div v-if="recipe.tags?.length" class="flex flex-wrap gap-2">
          <span
            v-for="tag in recipe.tags"
            :key="tag"
            class="px-2.5 py-1 text-xs bg-gradient-to-r from-violet-50 to-fuchsia-50 text-violet-700 rounded-full border border-violet-100"
          >
            {{ tag }}
          </span>
        </div>

        <!-- Ingredients -->
        <div v-if="recipe.ingredients?.length">
          <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span class="w-1 h-4 bg-gradient-to-b from-orange-400 to-rose-500 rounded-full"></span>
            食材清单
          </h3>
          <div class="bg-gray-50 rounded-2xl p-4 space-y-2">
            <div
              v-for="(ing, idx) in recipe.ingredients"
              :key="idx"
              class="flex items-center justify-between text-sm"
            >
              <span class="text-gray-700">{{ ing.name }}</span>
              <span class="text-gray-400">{{ ing.amount }}{{ ing.unit }}</span>
            </div>
          </div>
        </div>

        <!-- Instructions -->
        <div v-if="recipe.instructions?.length">
          <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span class="w-1 h-4 bg-gradient-to-b from-violet-400 to-fuchsia-500 rounded-full"></span>
            烹饪步骤
          </h3>
          <div class="space-y-3">
            <div
              v-for="(step, idx) in recipe.instructions"
              :key="idx"
              class="flex gap-3"
            >
              <div class="flex-shrink-0 w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white text-xs font-bold flex items-center justify-center shadow-md shadow-violet-500/20">
                {{ idx + 1 }}
              </div>
              <p class="text-sm text-gray-600 leading-relaxed pt-0.5">{{ step }}</p>
            </div>
          </div>
        </div>

        <!-- Step images -->
        <div v-if="getStepImages().length">
          <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span class="w-1 h-4 bg-gradient-to-b from-cyan-400 to-blue-500 rounded-full"></span>
            步骤图片
          </h3>
          <MediaGallery :media="getStepImages()" />
        </div>

        <!-- Links -->
        <div v-if="recipe.links?.length">
          <h3 class="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span class="w-1 h-4 bg-gradient-to-b from-green-400 to-emerald-500 rounded-full"></span>
            相关链接
          </h3>
          <div class="space-y-2">
            <a
              v-for="(link, idx) in recipe.links"
              :key="idx"
              :href="link.url"
              target="_blank"
              class="flex items-center gap-2 text-sm text-blue-500 hover:text-blue-700 hover:underline"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.318a4.5 4.5 0 00-1.242-7.244l4.5-4.5a4.5 4.5 0 016.364 6.364l-1.757 1.757" /></svg>
              <span class="truncate">{{ link.comment || link.url }}</span>
            </a>
          </div>
        </div>

        <!-- Action button -->
        <div class="pt-2 pb-1">
          <button
            @click="emit('order', recipe)"
            class="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all font-medium shadow-lg shadow-green-500/25"
          >
            加入购物车
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fade-in 0.25s ease-out; }
.animate-slide-up { animation: slide-up 0.35s cubic-bezier(0.16, 1, 0.3, 1); }
.animate-scale-in { animation: scale-in 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes slide-up { from { opacity: 0; transform: translateY(100%); } to { opacity: 1; transform: translateY(0); } }
@keyframes scale-in { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
