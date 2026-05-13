<script setup>
import { ref, onMounted } from 'vue'
import { recipesApi } from '../api/recipes'
import MediaUpload from './MediaUpload.vue'

const props = defineProps({
  entry: { type: Object, default: null },
})

const emit = defineEmits(['close', 'submit'])

const isEdit = !!props.entry

const form = ref({
  title: props.entry?.title || '',
  description: props.entry?.description || '',
  ingredients: props.entry?.ingredients?.length ? [...props.entry.ingredients] : [''],
  instructions: props.entry?.instructions?.length ? [...props.entry.instructions] : [''],
  prep_time_min: props.entry?.prep_time_min ?? null,
  cook_time_min: props.entry?.cook_time_min ?? null,
  servings: props.entry?.servings ?? null,
  tags: props.entry?.tags ? [...props.entry.tags] : [],
  price: props.entry?.price ?? 0,
  links: props.entry?.links?.length ? [...props.entry.links] : [{ url: '', comment: '' }],
})

const tagInput = ref('')
const submitting = ref(false)
const mediaList = ref([])

onMounted(async () => {
  if (props.entry) {
    try {
      const { data } = await recipesApi.listMedia(props.entry.id)
      mediaList.value = data
    } catch {}
  }
})

function addItem(list) {
  list.push('')
}

function removeItem(list, index) {
  if (list.length > 1) list.splice(index, 1)
}

function addTag() {
  const tag = tagInput.value.trim()
  if (tag && !form.value.tags.includes(tag)) {
    form.value.tags.push(tag)
  }
  tagInput.value = ''
}

function removeTag(index) {
  form.value.tags.splice(index, 1)
}

function addLink() {
  form.value.links.push({ url: '', comment: '' })
}

function removeLink(index) {
  if (form.value.links.length > 1) form.value.links.splice(index, 1)
}

async function handleUpload(file, mediaType) {
  await recipesApi.uploadMedia(props.entry.id, file, mediaType)
  const { data } = await recipesApi.listMedia(props.entry.id)
  mediaList.value = data
}

async function handleDeleteMedia(mediaId) {
  await recipesApi.deleteMedia(props.entry.id, mediaId)
  mediaList.value = mediaList.value.filter(m => m.id !== mediaId)
}

async function handleSubmit() {
  if (!form.value.title.trim()) return
  submitting.value = true
  try {
    const payload = {
      ...form.value,
      ingredients: form.value.ingredients.filter(i => typeof i === 'object' ? i.name?.trim() : i.trim()),
      instructions: form.value.instructions.filter(i => i.trim()),
      links: form.value.links.filter(l => l.url.trim()),
    }
    await emit('submit', payload)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold">{{ isEdit ? '编辑菜谱' : '新建菜谱' }}</h2>
          <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">菜名</label>
            <input
              v-model="form.title"
              type="text"
              required
              placeholder="红烧肉、番茄炒蛋..."
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">简介</label>
            <textarea
              v-model="form.description"
              rows="2"
              placeholder="简单描述一下这道菜..."
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            ></textarea>
          </div>

          <!-- 定价 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">定价（元）</label>
            <input
              v-model.number="form.price"
              type="number"
              min="0"
              step="0.01"
              placeholder="0"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">食材</label>
            <div class="space-y-2">
              <div v-for="(item, index) in form.ingredients" :key="index" class="flex gap-2">
                <input
                  v-model="form.ingredients[index]"
                  type="text"
                  :placeholder="`食材 ${index + 1}`"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  @click="removeItem(form.ingredients, index)"
                  class="px-2 py-2 text-gray-400 hover:text-red-500"
                >&times;</button>
              </div>
            </div>
            <button
              type="button"
              @click="addItem(form.ingredients)"
              class="mt-2 text-sm text-blue-500 hover:text-blue-700"
            >+ 添加食材</button>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">步骤</label>
            <div class="space-y-2">
              <div v-for="(item, index) in form.instructions" :key="index" class="flex gap-2">
                <span class="text-sm text-gray-400 pt-2 w-6">{{ index + 1 }}.</span>
                <textarea
                  v-model="form.instructions[index]"
                  rows="2"
                  :placeholder="`步骤 ${index + 1}`"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                ></textarea>
                <button
                  type="button"
                  @click="removeItem(form.instructions, index)"
                  class="px-2 text-gray-400 hover:text-red-500"
                >&times;</button>
              </div>
            </div>
            <button
              type="button"
              @click="addItem(form.instructions)"
              class="mt-2 text-sm text-blue-500 hover:text-blue-700"
            >+ 添加步骤</button>
          </div>

          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">准备 (分钟)</label>
              <input
                v-model.number="form.prep_time_min"
                type="number"
                min="0"
                placeholder="10"
                class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">烹饪 (分钟)</label>
              <input
                v-model.number="form.cook_time_min"
                type="number"
                min="0"
                placeholder="30"
                class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">份数</label>
              <input
                v-model.number="form.servings"
                type="number"
                min="1"
                placeholder="2"
                class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标签</label>
            <div class="flex gap-2 mb-2 flex-wrap">
              <span
                v-for="(tag, index) in form.tags"
                :key="tag"
                class="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded flex items-center gap-1"
              >
                {{ tag }}
                <button type="button" @click="removeTag(index)" class="hover:text-blue-900">&times;</button>
              </span>
            </div>
            <div class="flex gap-2">
              <input
                v-model="tagInput"
                type="text"
                placeholder="输入标签后回车"
                @keydown.enter.prevent="addTag"
                class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                @click="addTag"
                class="px-3 py-2 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
              >
                添加
              </button>
            </div>
          </div>

          <!-- 链接 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">相关链接</label>
            <div class="space-y-2">
              <div v-for="(link, index) in form.links" :key="index" class="flex gap-2">
                <input
                  v-model="link.url"
                  type="url"
                  placeholder="https://..."
                  class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  v-model="link.comment"
                  type="text"
                  placeholder="备注"
                  class="w-32 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  @click="removeLink(index)"
                  class="px-2 py-2 text-gray-400 hover:text-red-500"
                >&times;</button>
              </div>
            </div>
            <button
              type="button"
              @click="addLink"
              class="mt-2 text-sm text-blue-500 hover:text-blue-700"
            >+ 添加链接</button>
          </div>

          <!-- 媒体上传（仅编辑模式） -->
          <MediaUpload
            v-if="isEdit"
            :upload-fn="handleUpload"
            :existing-media="mediaList"
            @uploaded="() => {}"
            @delete-media="handleDeleteMedia"
          />

          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="emit('close')"
              class="flex-1 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="submitting || !form.title.trim()"
              class="flex-1 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {{ submitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
