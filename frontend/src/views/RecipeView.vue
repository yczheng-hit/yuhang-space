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

function getCoverImage(recipeId) {
  const media = mediaMap.value[recipeId]
  if (!media) return null
  const cover = media.find(m => m.media_type === 'cover' && m.file_type === 'image')
  return cover || media.find(m => m.file_type === 'image') || null
}

function getMediaUrl(filePath) {
  return `/media/${filePath}`
}

async function handleOrder(recipe) {
  const cartName = prompt('请输入购物车名称（留空使用默认购物车）:', '默认购物车')
  if (cartName === null) return
  const quantity = prompt('请输入数量:', '1')
  if (quantity === null) return
  try {
    const { default: axios } = await import('axios')
    const api = (await import('../api/index')).default
    await api.post('/orders', {
      recipe_id: recipe.id,
      cart_name: cartName || '默认购物车',
      quantity: parseInt(quantity) || 1,
    })
    alert(`已将「${recipe.title}」加入购物车「${cartName || '默认购物车'}」`)
  } catch (e) {
    alert('点菜失败: ' + (e.response?.data?.detail || e.message))
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">菜谱库</h1>
      <div class="flex gap-3">
        <router-link
          to="/orders"
          class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          点菜车
        </router-link>
        <button
          @click="openCreate"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          + 新建菜谱
        </button>
      </div>
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
            @click="handleOrder(recipe)"
            class="text-gray-300 hover:text-green-500 text-sm px-1"
            title="点菜"
          >
            🛒
          </button>
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

        <!-- 成品图缩略图 -->
        <div v-if="getCoverImage(recipe.id)" class="mb-3 rounded overflow-hidden h-40">
          <img
            :src="getMediaUrl(getCoverImage(recipe.id).file_path)"
            class="w-full h-full object-cover"
          />
        </div>

        <h3 class="text-lg font-semibold mb-2 pr-12">{{ recipe.title }}</h3>
        <p v-if="recipe.description" class="text-gray-600 text-sm mb-3">{{ recipe.description }}</p>

        <!-- 媒体展示（非封面图） -->
        <div v-if="mediaMap[recipe.id]?.length" class="mb-3">
          <MediaGallery :media="mediaMap[recipe.id]" />
        </div>

        <!-- 定价 -->
        <div v-if="recipe.price > 0" class="mb-2">
          <span class="text-orange-500 font-bold text-lg">¥{{ recipe.price.toFixed(2) }}</span>
        </div>

        <!-- 链接 -->
        <div v-if="recipe.links?.length" class="mb-3 space-y-1">
          <div v-for="(link, idx) in recipe.links" :key="idx" class="flex items-center gap-1 text-sm">
            <a :href="link.url" target="_blank" class="text-blue-500 hover:underline truncate max-w-[200px]">
              {{ link.url }}
            </a>
            <span v-if="link.comment" class="text-gray-400 text-xs">({{ link.comment }})</span>
          </div>
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
