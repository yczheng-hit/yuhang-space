<script setup>
import { ref } from 'vue'

const props = defineProps({
  recipe: { type: Object, required: true },
})

const emit = defineEmits(['close', 'submit'])

const cartName = ref('默认购物车')
const quantity = ref(1)
const note = ref('')
const submitting = ref(false)

async function handleSubmit() {
  submitting.value = true
  try {
    emit('submit', {
      recipe_id: props.recipe.id,
      cart_name: cartName.value || '默认购物车',
      quantity: quantity.value,
      note: note.value || undefined,
    })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 backdrop-blur-md flex items-end sm:items-center justify-center z-[55] animate-fade-in" @click.self="emit('close')">
    <div class="bg-white w-full sm:max-w-sm sm:rounded-3xl rounded-t-3xl shadow-2xl animate-slide-up sm:animate-scale-in">
      <!-- Drag handle mobile -->
      <div class="flex justify-center pt-3 sm:hidden">
        <div class="w-10 h-1 bg-gray-300 rounded-full"></div>
      </div>

      <div class="p-5 sm:p-6">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-gray-800">加入购物车</h2>
          <button @click="emit('close')" class="w-8 h-8 flex items-center justify-center rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all text-xl">&times;</button>
        </div>

        <!-- Recipe info -->
        <div class="flex items-center gap-3 mb-5 p-3 bg-gray-50 rounded-xl">
          <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-400 to-rose-500 flex items-center justify-center text-white text-lg shadow-md">
            🍳
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-semibold text-gray-800 truncate">{{ recipe.title }}</div>
            <div v-if="recipe.price > 0" class="text-orange-500 text-sm font-bold">¥{{ recipe.price.toFixed(2) }}</div>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Cart name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">购物车名称</label>
            <input
              v-model="cartName"
              type="text"
              placeholder="默认购物车"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-400 transition-all bg-white shadow-sm text-sm"
            />
          </div>

          <!-- Quantity -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">数量</label>
            <div class="flex items-center gap-3">
              <button
                type="button"
                @click="quantity = Math.max(1, quantity - 1)"
                class="w-10 h-10 rounded-xl border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50 active:bg-gray-100 transition-all text-lg font-bold"
              >
                −
              </button>
              <input
                v-model.number="quantity"
                type="number"
                min="1"
                class="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-400 transition-all bg-white shadow-sm text-sm text-center font-semibold"
              />
              <button
                type="button"
                @click="quantity++"
                class="w-10 h-10 rounded-xl border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50 active:bg-gray-100 transition-all text-lg font-bold"
              >
                +
              </button>
            </div>
          </div>

          <!-- Note -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">备注 <span class="text-gray-400 font-normal">(可选)</span></label>
            <input
              v-model="note"
              type="text"
              placeholder="例如：少辣、多加醋..."
              class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-400 transition-all bg-white shadow-sm text-sm"
            />
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="submitting"
            class="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 transition-all font-medium shadow-lg shadow-green-500/25 hover:shadow-xl hover:shadow-green-500/30"
          >
            {{ submitting ? '添加中...' : '确认添加' }}
          </button>
        </form>
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
