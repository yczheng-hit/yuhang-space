<script setup>
import { ref, onMounted } from 'vue'
import { ordersApi } from '../api/orders'
import { recipesApi } from '../api/recipes'

const carts = ref([])
const currentCart = ref('默认购物车')
const cartData = ref(null)
const loading = ref(false)
const recipes = ref({})
const newCartName = ref('')

// History
const historyBatches = ref([])
const showHistory = ref(false)
const expandedBatch = ref(null)
const batchData = ref(null)
const batchLoading = ref(false)

async function loadCarts() {
  try {
    const { data } = await ordersApi.listCarts()
    carts.value = data
    if (!data.includes(currentCart.value) && data.length > 0) {
      currentCart.value = data[0]
    }
  } catch {}
}

async function loadHistory() {
  try {
    const { data } = await ordersApi.listHistory()
    historyBatches.value = data
  } catch {}
}

async function loadCartData() {
  loading.value = true
  try {
    const { data } = await ordersApi.getCart(currentCart.value)
    cartData.value = data
    await ensureRecipes(data.items)
  } catch {
    cartData.value = null
  } finally {
    loading.value = false
  }
}

async function loadBatchData(submittedAt) {
  if (expandedBatch.value === submittedAt) {
    expandedBatch.value = null
    batchData.value = null
    return
  }
  batchLoading.value = true
  expandedBatch.value = submittedAt
  try {
    const { data } = await ordersApi.getHistory(submittedAt)
    batchData.value = data
    await ensureRecipes(data.items)
  } catch {
    batchData.value = null
  } finally {
    batchLoading.value = false
  }
}

async function ensureRecipes(items) {
  for (const item of items) {
    if (!recipes.value[item.recipe_id]) {
      try {
        const { data: allRecipes } = await recipesApi.list()
        for (const r of allRecipes) recipes.value[r.id] = r
      } catch {}
    }
  }
}

async function switchCart(name) {
  currentCart.value = name
  showHistory.value = false
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
  showHistory.value = false
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

async function submitCart() {
  if (!cartData.value || cartData.value.items.length === 0) return
  if (!confirm(`确定提交购物车「${currentCart.value}」？提交后将移入历史订单。`)) return
  try {
    await ordersApi.submitCart(currentCart.value)
    await loadCartData()
    await loadCarts()
    await loadHistory()
    alert('提交成功！')
  } catch (e) {
    alert('提交失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteBatch(submittedAt) {
  if (!confirm('确定删除此历史订单？')) return
  try {
    await ordersApi.deleteHistory(submittedAt)
    if (expandedBatch.value === submittedAt) {
      expandedBatch.value = null
      batchData.value = null
    }
    await loadHistory()
  } catch (e) {
    alert('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

function toggleHistory() {
  showHistory.value = !showHistory.value
  if (showHistory.value) {
    loadHistory()
  }
}

function getRecipeTitle(recipeId) {
  return recipes.value[recipeId]?.title || '未知菜品'
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const month = (d.getMonth() + 1).toString().padStart(2, '0')
  const day = d.getDate().toString().padStart(2, '0')
  const hour = d.getHours().toString().padStart(2, '0')
  const min = d.getMinutes().toString().padStart(2, '0')
  return `${month}-${day} ${hour}:${min}`
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
}

onMounted(async () => {
  await loadCarts()
  await loadCartData()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">购物车</h1>
      <div class="flex gap-2">
        <button
          @click="toggleHistory"
          class="px-4 py-2 text-sm rounded-lg transition-all"
          :class="showHistory
            ? 'bg-violet-500 text-white shadow-md'
            : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'"
        >
          历史订单
        </button>
        <router-link
          to="/recipes"
          class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 text-sm"
        >
          返回菜谱
        </router-link>
      </div>
    </div>

    <!-- Cart tabs -->
    <div class="mb-6" v-if="!showHistory">
      <div class="flex items-center gap-2 flex-wrap mb-3">
        <span class="text-sm font-medium text-gray-700">购物车:</span>
        <button
          v-for="cart in carts"
          :key="cart"
          @click="switchCart(cart)"
          :class="[
            'px-3 py-1.5 rounded-lg text-sm transition-all',
            currentCart === cart
              ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-md shadow-green-500/25'
              : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
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
            class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm w-36 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-400"
          />
          <button
            @click="createCart"
            class="px-3 py-1.5 bg-green-50 text-green-600 rounded-lg text-sm hover:bg-green-100 border border-green-200"
          >
            新建
          </button>
        </div>
      </div>
    </div>

    <!-- Active cart -->
    <div v-if="!showHistory">
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

      <div v-else-if="!cartData || cartData.items.length === 0" class="text-center py-12 text-gray-400">
        <div class="text-4xl mb-3">🛒</div>
        <p>购物车为空，去菜谱页面选购吧</p>
      </div>

      <div v-else>
        <div class="space-y-3 mb-4">
          <div
            v-for="item in cartData.items"
            :key="item.id"
            class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between"
          >
            <div class="flex-1 min-w-0">
              <h3 class="font-medium text-gray-800 truncate">{{ getRecipeTitle(item.recipe_id) }}</h3>
              <p v-if="item.note" class="text-sm text-gray-500 truncate">{{ item.note }}</p>
              <p class="text-sm text-orange-500 font-medium mt-1">
                ¥{{ item.unit_price.toFixed(2) }} × {{ item.quantity }}
                = ¥{{ (item.unit_price * item.quantity).toFixed(2) }}
              </p>
            </div>
            <div class="flex items-center gap-2 ml-4">
              <div class="flex items-center gap-1 bg-gray-50 rounded-lg p-1">
                <button
                  @click="updateQuantity(item.id, item.quantity - 1)"
                  :disabled="item.quantity <= 1"
                  class="w-7 h-7 rounded-md flex items-center justify-center text-gray-500 hover:bg-white disabled:opacity-30 transition-all text-sm font-bold"
                >
                  −
                </button>
                <span class="w-8 text-center text-sm font-semibold">{{ item.quantity }}</span>
                <button
                  @click="updateQuantity(item.id, item.quantity + 1)"
                  class="w-7 h-7 rounded-md flex items-center justify-center text-gray-500 hover:bg-white transition-all text-sm font-bold"
                >
                  +
                </button>
              </div>
              <button
                @click="deleteOrder(item.id)"
                class="text-gray-300 hover:text-red-500 text-xl px-1 transition-colors"
                title="删除"
              >
                &times;
              </button>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
          <div class="flex justify-between items-center mb-4">
            <span class="text-gray-500">共 {{ cartData.item_count }} 项</span>
            <span class="text-xl font-bold text-orange-500">
              合计: ¥{{ cartData.total_price.toFixed(2) }}
            </span>
          </div>
          <div class="flex gap-3">
            <button
              @click="clearCurrentCart"
              class="flex-1 py-2.5 border border-gray-200 text-gray-500 rounded-xl hover:bg-gray-50 transition-all text-sm"
            >
              清空购物车
            </button>
            <button
              @click="submitCart"
              class="flex-1 py-2.5 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all font-medium shadow-lg shadow-green-500/25 text-sm"
            >
              提交订单
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- History section -->
    <div v-if="showHistory">
      <div v-if="historyBatches.length === 0" class="text-center py-12 text-gray-400">
        <div class="text-4xl mb-3">📋</div>
        <p>暂无历史订单</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="batch in historyBatches"
          :key="batch.submitted_at"
          class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
        >
          <!-- Batch header -->
          <div
            @click="loadBatchData(batch.submitted_at)"
            class="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-all"
          >
            <div class="flex items-center gap-3">
              <span class="text-lg">📦</span>
              <div>
                <div class="font-medium text-gray-800">{{ batch.cart_name }}</div>
                <div class="text-xs text-gray-400">{{ formatTime(batch.submitted_at) }}</div>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="text-right">
                <div class="text-sm text-gray-500">{{ batch.item_count }} 项</div>
                <div class="text-sm font-bold text-orange-500">¥{{ batch.total_price.toFixed(2) }}</div>
              </div>
              <button
                @click.stop="deleteBatch(batch.submitted_at)"
                class="text-gray-300 hover:text-red-500 text-sm px-1 transition-colors"
                title="删除"
              >
                🗑
              </button>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4 text-gray-400 transition-transform"
                :class="{ 'rotate-180': expandedBatch === batch.submitted_at }"
                fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </div>
          </div>

          <!-- Batch detail (expandable) -->
          <div v-if="expandedBatch === batch.submitted_at" class="border-t border-gray-100">
            <div v-if="batchLoading" class="p-4 text-center text-gray-400 text-sm">加载中...</div>
            <div v-else-if="batchData" class="p-4 space-y-2">
              <div
                v-for="item in batchData.items"
                :key="item.id"
                class="flex items-center justify-between text-sm py-1.5"
              >
                <div class="flex-1 min-w-0">
                  <span class="text-gray-700 truncate block">{{ getRecipeTitle(item.recipe_id) }}</span>
                  <span v-if="item.note" class="text-gray-400 text-xs">{{ item.note }}</span>
                </div>
                <span class="text-gray-500 ml-4 flex-shrink-0">
                  ¥{{ item.unit_price.toFixed(2) }} × {{ item.quantity }}
                  = <span class="font-medium">¥{{ (item.unit_price * item.quantity).toFixed(2) }}</span>
                </span>
              </div>
              <div class="border-t border-gray-100 pt-2 flex justify-between items-center">
                <span class="text-gray-400 text-xs">共 {{ batchData.item_count }} 项</span>
                <span class="font-bold text-orange-500">¥{{ batchData.total_price.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
