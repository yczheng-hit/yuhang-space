import { defineStore } from 'pinia'
import { ref } from 'vue'
import { recipesApi } from '../api/recipes'

export const useRecipeStore = defineStore('recipe', () => {
  const recipes = ref([])
  const loading = ref(false)

  async function fetchRecipes() {
    loading.value = true
    try {
      const { data } = await recipesApi.list()
      recipes.value = data
    } finally {
      loading.value = false
    }
  }

  async function createRecipe(recipeData) {
    const { data } = await recipesApi.create(recipeData)
    recipes.value.unshift(data)
    return data
  }

  async function updateRecipe(id, recipeData) {
    const { data } = await recipesApi.update(id, recipeData)
    const index = recipes.value.findIndex((r) => r.id === id)
    if (index !== -1) recipes.value[index] = data
    return data
  }

  async function deleteRecipe(id) {
    await recipesApi.delete(id)
    recipes.value = recipes.value.filter((r) => r.id !== id)
  }

  return { recipes, loading, fetchRecipes, createRecipe, updateRecipe, deleteRecipe }
})
