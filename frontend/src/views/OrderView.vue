<script setup>
import { ref, onMounted, computed } from 'vue'
import { ordersApi } from '../api/orders'
import { recipesApi } from '../api/recipes'

const carts = ref([])
const currentCart = ref('默认购物车')
const cartData = ref(null)
const loading = ref(false)
const recipes = ref({})
const newCartName = ref('')

async function loadCarts() {
  try {
    const { data } = await ordersApi.listCarts()
    carts.value = data
    if (!data.includes(currentCart.value) && data.length > 0) {
      currentCart.value = data[0]
    }
  } catch {}
}

async function loadCartData() {
  loading.value = true
  try {
    const { data } = await ordersApi.getCart(currentCart.value)
    cartData.value = data
    // Load recipe info for each item
    for (const item of data.items) {
      if (!recipes.value[item.recipe_id]) {
        try {
          const { data: recipe } = await recipesApi.list()
          const found = recipe.find(r => r.id === item.recipe_id)
          if (found) recipes.value[item.recipe_id] = found
        } catch {}
      }
    }
  } catch {
    cartData.value = null
  } finally {
    loading.value = false
  }
}

async function switchCart(name) {
  currentCart.value = name
  await loadCartData()
}

async function createCart() {
  const name = newCartName.value.trim()
  if (!name) return
  if (carts.value.includes(name)) {
    alert('购物车已存在')
    return
  }
  carts.value.push(name)
  currentCart.value = name
  newCartName.value = ''
  cartData.value = { cart_name: name, items: [], total_price: 0, item_count: 0 }
}

async function updateQuantity(orderId, quantity) {
  if (quantity < 1) return
  try {
    await ordersApi.updateOrder(orderId, { quantity })
    await loadCartData()
  } catch (e) {
    alert('更新失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteOrder(orderId) {
  if (!confirm('确定删除此菜品？')) return
  try {
    await ordersApi.deleteOrder(orderId)
    await loadCartData()
    await loadCarts()
  } catch (e) {
    alert('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function clearCurrentCart() {
  if (!confirm(`确定清空购物车「${currentCart.value}」？`)) return
  try {
    await ordersApi.clearCart(currentCart.value)
    await loadCartData()
    await loadCarts()
  } catch (e) {
    alert('清空失败: ' + (e.response?.data?.detail || e.message))
  }
}

function getRecipeTitle(recipeId) {
  return recipes.value[recipeId]?.title || '未知菜品'
}

onMounted(async () => {
  await loadCarts()
  await loadCartData()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">点菜车</h1>
      <router-link
        to="/recipes"
        class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
      >
        返回菜谱
      </router-link>
    </div>

    <!-- 购物车选择 -->
    <div class="mb-6">
      <div class="flex items-center gap-2 flex-wrap mb-3">
        <span class="text-sm font-medium text-gray-700">购物车:</span>
        <button
          v-for="cart in carts"
          :key="cart"
          @click="switchCart(cart)"
          :class="[
            'px-3 py-1 rounded text-sm transition-colors',
            currentCart === cart
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ cart }}
        </button>
        <div class="flex gap-1">
          <input
            v-model="newCartName"
            type="text"
            placeholder="新购物车名称"
            @keydown.enter.prevent="createCart"
            class="px-2 py-1 border border-gray-300 rounded text-sm w-32 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            @click="createCart"
            class="px-2 py-1 bg-blue-100 text-blue-600 rounded text-sm hover:bg-blue-200"
          >
            新建
          </button>
        </div>
      </div>
    </div>

    <!-- 购物车内容 -->
    <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

    <div v-else-if="!cartData || cartData.items.length === 0" class="text-center py-12 text-gray-400">
      购物车为空，去菜谱页面点菜吧
    </div>

    <div v-else>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">{{ currentCart }}</h2>
        <button
          @click="clearCurrentCart"
          class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
        >
          一键清空
        </button>
      </div>

      <div class="space-y-3">
        <div
          v-for="item in cartData.items"
          :key="item.id"
          class="bg-white p-4 rounded-lg shadow flex items-center justify-between"
        >
          <div class="flex-1">
            <h3 class="font-medium">{{ getRecipeTitle(item.recipe_id) }}</h3>
            <p v-if="item.note" class="text-sm text-gray-500">{{ item.note }}</p>
            <p class="text-sm text-orange-500">
              ¥{{ item.unit_price.toFixed(2) }} × {{ item.quantity }}
              = ¥{{ (item.unit_price * item.quantity).toFixed(2) }}
            </p>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-1">
              <button
                @click="updateQuantity(item.id, item.quantity - 1)"
                :disabled="item.quantity <= 1"
                class="w-8 h-8 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
              >
                -
              </button>
              <span class="w-8 text-center">{{ item.quantity }}</span>
              <button
                @click="updateQuantity(item.id, item.quantity + 1)"
                class="w-8 h-8 bg-gray-100 rounded hover:bg-gray-200"
              >
                +
              </button>
            </div>
            <button
              @click="deleteOrder(item.id)"
              class="text-red-400 hover:text-red-600 text-xl px-2"
              title="删除"
            >
              &times;
            </button>
          </div>
        </div>
      </div>

      <!-- 汇总 -->
      <div class="mt-6 p-4 bg-gray-50 rounded-lg">
        <div class="flex justify-between items-center">
          <span class="text-gray-600">共 {{ cartData.item_count }} 项</span>
          <span class="text-xl font-bold text-orange-500">
            合计: ¥{{ cartData.total_price.toFixed(2) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
