<script setup>
import { onMounted } from 'vue'
import { useRecipeStore } from '../stores/recipe'

const store = useRecipeStore()

onMounted(() => {
  store.fetchRecipes()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">菜谱库</h1>
      <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
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
        class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <h3 class="text-lg font-semibold mb-2">{{ recipe.title }}</h3>
        <p v-if="recipe.description" class="text-gray-600 text-sm mb-3">{{ recipe.description }}</p>

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
  </div>
</template>
