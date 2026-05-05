<script setup>
import { ref, onMounted } from 'vue'
import { useRecipeStore } from '../stores/recipe'
import { recipesApi } from '../api/recipes'
import RecipeFormModal from '../components/RecipeFormModal.vue'
import MediaGallery from '../components/MediaGallery.vue'

const store = useRecipeStore()
const showModal = ref(false)
const editingEntry = ref(null)
const mediaMap = ref({})

onMounted(async () => {
  await store.fetchRecipes()
  for (const recipe of store.recipes) {
    try {
      const { data } = await recipesApi.listMedia(recipe.id)
      if (data.length) mediaMap.value[recipe.id] = data
    } catch {}
  }
})

function openCreate() {
  editingEntry.value = null
  showModal.value = true
}

function openEdit(recipe) {
  editingEntry.value = recipe
  showModal.value = true
}

async function handleSubmit(data) {
  if (editingEntry.value) {
    await store.updateRecipe(editingEntry.value.id, data)
    const { data: media } = await recipesApi.listMedia(editingEntry.value.id)
    mediaMap.value[editingEntry.value.id] = media
  } else {
    await store.createRecipe(data)
  }
  showModal.value = false
  editingEntry.value = null
}

async function handleDelete(id) {
  if (confirm('确定删除这个菜谱？')) {
    await store.deleteRecipe(id)
    delete mediaMap.value[id]
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">菜谱库</h1>
      <button
        @click="openCreate"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        + 新建菜谱
      </button>
    </div>

    <div v-if="store.loading" class="text-center py-8 text-gray-500">加载中...</div>

    <div v-else-if="store.recipes.length === 0" class="text-center py-12 text-gray-400">
      暂无菜谱，点击上方按钮创建
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="recipe in store.recipes"
        :key="recipe.id"
        class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow relative"
      >
        <div class="absolute top-3 right-3 flex items-center gap-1">
          <button
            @click="openEdit(recipe)"
            class="text-gray-300 hover:text-blue-500 text-lg px-1"
            title="编辑"
          >
            ✎
          </button>
          <button
            @click="handleDelete(recipe.id)"
            class="text-gray-300 hover:text-red-500 text-xl px-1"
            title="删除"
          >
            &times;
          </button>
        </div>

        <h3 class="text-lg font-semibold mb-2 pr-12">{{ recipe.title }}</h3>
        <p v-if="recipe.description" class="text-gray-600 text-sm mb-3">{{ recipe.description }}</p>

        <!-- 媒体展示 -->
        <div v-if="mediaMap[recipe.id]?.length" class="mb-3">
          <MediaGallery :media="mediaMap[recipe.id]" />
        </div>

        <div class="flex flex-wrap gap-2 mb-3">
          <span
            v-for="tag in recipe.tags"
            :key="tag"
            class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
          >
            {{ tag }}
          </span>
        </div>

        <div class="flex items-center gap-4 text-sm text-gray-500">
          <span v-if="recipe.prep_time_min">准备 {{ recipe.prep_time_min }} 分钟</span>
          <span v-if="recipe.cook_time_min">烹饪 {{ recipe.cook_time_min }} 分钟</span>
          <span v-if="recipe.servings">{{ recipe.servings }} 人份</span>
        </div>
      </div>
    </div>

    <RecipeFormModal
      v-if="showModal"
      :entry="editingEntry"
      @close="showModal = false; editingEntry = null"
      @submit="handleSubmit"
    />
  </div>
</template>
