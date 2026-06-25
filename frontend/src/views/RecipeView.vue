<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRecipeStore } from '../stores/recipe'
import { recipesApi } from '../api/recipes'
import RecipeFormModal from '../components/RecipeFormModal.vue'
import RecipeDetailModal from '../components/RecipeDetailModal.vue'
import OrderModal from '../components/OrderModal.vue'

const store = useRecipeStore()
const showModal = ref(false)
const editingEntry = ref(null)
const mediaMap = ref({})

// Detail modal
const detailRecipe = ref(null)

// Order modal
const orderRecipe = ref(null)

// Tag filter
const activeTag = ref(null)
const searchQuery = ref('')

// Collect all unique tags from recipes
const allTags = computed(() => {
  const tagSet = new Set()
  for (const recipe of store.recipes) {
    if (recipe.tags) {
      recipe.tags.forEach(t => tagSet.add(t))
    }
  }
  return [...tagSet].sort()
})

// Filtered recipes (search + tag)
const filteredRecipes = computed(() => {
  let list = store.recipes
  if (activeTag.value) {
    list = list.filter(r => r.tags?.includes(activeTag.value))
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(r =>
      r.title?.toLowerCase().includes(q) ||
      r.description?.toLowerCase().includes(q) ||
      r.tags?.some(t => t.toLowerCase().includes(q))
    )
  }
  return list
})

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

function openEdit(recipe, event) {
  event.stopPropagation()
  editingEntry.value = recipe
  showModal.value = true
}

function openDetail(recipe) {
  detailRecipe.value = recipe
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

async function handleDelete(id, event) {
  event.stopPropagation()
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

function openOrder(recipe, event) {
  if (event) event.stopPropagation()
  orderRecipe.value = recipe
}

async function handleOrderSubmit(orderData) {
  try {
    const api = (await import('../api/index')).default
    await api.post('/orders', orderData)
    const title = orderRecipe.value?.title || '菜谱'
    orderRecipe.value = null
    alert(`已将「${title}」加入购物车`)
  } catch (e) {
    alert('加入购物车失败: ' + (e.response?.data?.detail || e.message))
  }
}

function handleDetailOrder(recipe) {
  detailRecipe.value = null
  orderRecipe.value = recipe
}

function toggleTag(tag) {
  activeTag.value = activeTag.value === tag ? null : tag
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
          购物车
        </router-link>
        <button
          @click="openCreate"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          + 新建菜谱
        </button>
      </div>
    </div>

    <!-- Search bar -->
    <div class="mb-4">
      <div class="relative">
        <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" /></svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索菜谱名称、描述、标签..."
          class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-400 transition-all bg-white/70 shadow-sm text-sm"
        />
        <button
          v-if="searchQuery"
          @click="searchQuery = ''"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          &times;
        </button>
      </div>
    </div>

    <!-- Tag filter bar -->
    <div v-if="allTags.length" class="mb-5 flex flex-wrap gap-2">
      <button
        @click="activeTag = null"
        class="px-3 py-1.5 text-sm rounded-full transition-all duration-200"
        :class="activeTag === null
          ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-md shadow-violet-500/25'
          : 'bg-white/70 text-gray-600 hover:bg-white border border-gray-200'"
      >
        全部
      </button>
      <button
        v-for="tag in allTags"
        :key="tag"
        @click="toggleTag(tag)"
        class="px-3 py-1.5 text-sm rounded-full transition-all duration-200"
        :class="activeTag === tag
          ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-md shadow-violet-500/25'
          : 'bg-white/70 text-gray-600 hover:bg-white border border-gray-200'"
      >
        {{ tag }}
      </button>
    </div>

    <div v-if="store.loading" class="text-center py-8 text-gray-500">加载中...</div>

    <div v-else-if="filteredRecipes.length === 0" class="text-center py-12 text-gray-400">
      {{ searchQuery ? `没有找到「${searchQuery}」相关的菜谱` : activeTag ? `没有「${activeTag}」标签的菜谱` : '暂无菜谱，点击上方按钮创建' }}
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="recipe in filteredRecipes"
        :key="recipe.id"
        @click="openDetail(recipe)"
        class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow relative cursor-pointer group"
      >
        <div class="absolute top-3 right-3 flex items-center gap-1 z-10">
          <button
            @click.stop="openOrder(recipe, $event)"
            class="text-gray-300 hover:text-green-500 text-sm px-1"
            title="加入购物车"
          >
            🛒
          </button>
          <button
            @click.stop="openEdit(recipe, $event)"
            class="text-gray-300 hover:text-blue-500 text-lg px-1"
            title="编辑"
          >
            ✎
          </button>
          <button
            @click.stop="handleDelete(recipe.id, $event)"
            class="text-gray-300 hover:text-red-500 text-xl px-1"
            title="删除"
          >
            &times;
          </button>
        </div>

        <!-- Cover thumbnail -->
        <div v-if="getCoverImage(recipe.id)" class="mb-3 rounded overflow-hidden h-40">
          <img
            :src="getMediaUrl(getCoverImage(recipe.id).file_path)"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>

        <h3 class="text-lg font-semibold mb-2 pr-12">{{ recipe.title }}</h3>
        <p v-if="recipe.description" class="text-gray-600 text-sm mb-3 line-clamp-2">{{ recipe.description }}</p>

        <!-- Price -->
        <div v-if="recipe.price > 0" class="mb-2">
          <span class="text-orange-500 font-bold text-lg">¥{{ recipe.price.toFixed(2) }}</span>
        </div>

        <!-- Tags -->
        <div v-if="recipe.tags?.length" class="flex flex-wrap gap-2 mb-3">
          <span
            v-for="tag in recipe.tags"
            :key="tag"
            class="px-2 py-1 text-xs rounded"
            :class="activeTag === tag
              ? 'bg-violet-100 text-violet-700 font-medium'
              : 'bg-gray-100 text-gray-600'"
          >
            {{ tag }}
          </span>
        </div>

        <div class="flex items-center gap-4 text-sm text-gray-500">
          <span v-if="recipe.prep_time_min">准备 {{ recipe.prep_time_min }} 分钟</span>
          <span v-if="recipe.cook_time_min">烹饪 {{ recipe.cook_time_min }} 分钟</span>
          <span v-if="recipe.servings">{{ recipe.servings }} 人份</span>
        </div>

        <!-- Click hint -->
        <div class="mt-3 text-xs text-gray-400 group-hover:text-violet-500 transition-colors">
          点击查看详情 →
        </div>
      </div>
    </div>

    <RecipeFormModal
      v-if="showModal"
      :entry="editingEntry"
      @close="showModal = false; editingEntry = null"
      @submit="handleSubmit"
    />

    <RecipeDetailModal
      v-if="detailRecipe"
      :recipe="detailRecipe"
      @close="detailRecipe = null"
      @order="handleDetailOrder"
    />

    <OrderModal
      v-if="orderRecipe"
      :recipe="orderRecipe"
      @close="orderRecipe = null"
      @submit="handleOrderSubmit"
    />
  </div>
</template>
