<template>
  <div class="space-y-6">
    <!-- Categories Section -->
    <section class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-bold text-zinc-900">Категории</h2>
        <button
          @click="fetchMenu"
          class="text-xs bg-zinc-100 hover:bg-zinc-200 px-3 py-1.5 rounded-xl font-bold text-zinc-700"
        >
          🔄 Обновить
        </button>
      </div>

      <div v-if="isLoading && !categories.length" class="text-center py-8 text-zinc-400 text-xs">
        Загрузка меню...
      </div>

      <div v-else-if="error" class="bg-red-50 text-red-600 text-xs p-3 rounded-xl font-medium text-center">
        {{ error }}
      </div>

      <div v-else class="grid grid-cols-3 gap-2.5">
        <button
          v-for="cat in categories"
          :key="cat.id"
          @click="openEditCategory(cat)"
          class="flex flex-col items-center gap-1"
        >
          <div class="w-full aspect-square rounded-2xl overflow-hidden bg-zinc-100 border border-zinc-200 relative">
            <img v-if="cat.image_url" :src="imgSrc(cat.image_url)" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-2xl">🍽️</div>
            <span class="absolute bottom-1 right-1 bg-white/90 rounded-lg w-5 h-5 flex items-center justify-center text-[10px]">✏️</span>
          </div>
          <span class="text-[11px] font-bold text-zinc-700 text-center leading-tight line-clamp-2">{{ cat.name }}</span>
        </button>

        <button @click="openCreateCategory" class="flex flex-col items-center gap-1">
          <div class="w-full aspect-square rounded-2xl border-2 border-dashed border-zinc-300 flex items-center justify-center text-zinc-400 text-2xl">
            +
          </div>
          <span class="text-[11px] font-bold text-zinc-400">Добавить</span>
        </button>
      </div>

      <!-- Category Form Panel -->
      <div v-if="showCategoryForm" class="bg-white rounded-2xl p-4 shadow-sm border border-amber-200 space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-bold text-zinc-900">{{ categoryForm.id ? 'Изменить категорию' : 'Новая категория' }}</h3>
          <button @click="showCategoryForm = false" class="text-zinc-400 text-xs font-bold">✕</button>
        </div>

        <div class="flex items-center gap-3">
          <div
            @click="categoryFileInput?.click()"
            class="w-16 h-16 rounded-xl bg-zinc-100 overflow-hidden flex items-center justify-center cursor-pointer border border-zinc-200 flex-shrink-0"
          >
            <img v-if="categoryPreview" :src="categoryPreview" class="w-full h-full object-cover" />
            <span v-else class="text-xl text-zinc-400">📷</span>
          </div>
          <input ref="categoryFileInput" type="file" accept="image/*" class="hidden" @change="handleCategoryFileChange" />
          <input
            v-model="categoryForm.name"
            type="text"
            placeholder="Название категории"
            class="flex-1 px-3 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>

        <p v-if="categoryError" class="text-xs text-red-600 font-bold">{{ categoryError }}</p>

        <button
          @click="saveCategory"
          :disabled="isSavingCategory || !categoryForm.name.trim()"
          class="w-full py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-zinc-300 text-white font-bold text-sm rounded-xl active:scale-[0.98] transition-all"
        >
          {{ isSavingCategory ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </section>

    <!-- Items Section -->
    <section class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-bold text-zinc-900">Блюда</h2>
        <button
          @click="openCreateItem"
          :disabled="!categories.length"
          class="text-xs bg-amber-500 hover:bg-amber-600 disabled:bg-zinc-300 text-white px-3 py-1.5 rounded-xl font-bold"
        >
          + Добавить блюдо
        </button>
      </div>

      <!-- Item Form Panel -->
      <div v-if="showItemForm" class="bg-white rounded-2xl p-4 shadow-sm border border-amber-200 space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-bold text-zinc-900">{{ itemForm.id ? 'Изменить блюдо' : 'Новое блюдо' }}</h3>
          <button @click="showItemForm = false" class="text-zinc-400 text-xs font-bold">✕</button>
        </div>

        <div class="flex items-center gap-3">
          <div
            @click="itemFileInput?.click()"
            class="w-16 h-16 rounded-xl bg-zinc-100 overflow-hidden flex items-center justify-center cursor-pointer border border-zinc-200 flex-shrink-0"
          >
            <img v-if="itemPreview" :src="itemPreview" class="w-full h-full object-cover" />
            <span v-else class="text-xl text-zinc-400">📷</span>
          </div>
          <input ref="itemFileInput" type="file" accept="image/*" class="hidden" @change="handleItemFileChange" />
          <div class="flex-1 space-y-2">
            <input
              v-model="itemForm.name"
              type="text"
              placeholder="Название блюда"
              class="w-full px-3 py-2 bg-zinc-50 border border-zinc-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
            <input
              v-model.number="itemForm.price"
              type="number"
              placeholder="Цена, ₩"
              class="w-full px-3 py-2 bg-zinc-50 border border-zinc-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>
        </div>

        <textarea
          v-model="itemForm.description"
          rows="2"
          placeholder="Описание"
          class="w-full px-3 py-2 bg-zinc-50 border border-zinc-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-amber-500"
        ></textarea>

        <select v-model.number="itemForm.category_id" class="w-full px-3 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-sm font-semibold">
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>

        <label class="flex items-center gap-2 text-xs font-bold text-zinc-700">
          <input type="checkbox" v-model="itemForm.is_available" class="w-4 h-4 accent-amber-500" />
          Доступно в меню
        </label>

        <p v-if="itemError" class="text-xs text-red-600 font-bold">{{ itemError }}</p>

        <button
          @click="saveItem"
          :disabled="isSavingItem || !itemForm.name.trim() || !itemForm.price"
          class="w-full py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-zinc-300 text-white font-bold text-sm rounded-xl active:scale-[0.98] transition-all"
        >
          {{ isSavingItem ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>

      <div v-if="!isLoading && !categories.length" class="text-center py-8 text-zinc-400 text-xs">
        Сначала добавьте категорию
      </div>

      <div
        v-for="cat in categories"
        :key="cat.id"
        class="bg-white rounded-2xl p-4 shadow-sm border border-zinc-100 space-y-3"
      >
        <h3 class="text-xs font-bold text-amber-600 uppercase tracking-wider border-b border-zinc-100 pb-2">
          {{ cat.name }}
        </h3>

        <div v-if="!cat.items.length" class="text-xs text-zinc-400 py-2">Блюд пока нет</div>

        <div class="divide-y divide-zinc-100">
          <div v-for="item in cat.items" :key="item.id" class="py-3 first:pt-0 last:pb-0 flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl overflow-hidden bg-zinc-100 flex-shrink-0 flex items-center justify-center">
              <img v-if="item.image_url" :src="imgSrc(item.image_url)" class="w-full h-full object-cover" />
              <span v-else class="text-lg">🍲</span>
            </div>

            <div class="flex-1 min-w-0" :class="{ 'opacity-50': !item.is_available }">
              <div class="font-bold text-sm text-zinc-900 truncate">{{ item.name }}</div>
              <div class="text-xs text-amber-600 font-semibold mt-0.5">
                {{ item.price.toLocaleString('ko-KR') }} ₩
              </div>
            </div>

            <button
              @click="openEditItem(item, cat.id)"
              class="w-8 h-8 flex items-center justify-center rounded-lg bg-zinc-100 text-zinc-600 text-sm flex-shrink-0"
            >
              ✏️
            </button>

            <!-- Availability Toggle Switch -->
            <button
              @click="toggleItem(item)"
              class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
              :class="item.is_available ? 'bg-emerald-500' : 'bg-zinc-300'"
            >
              <span
                class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                :class="item.is_available ? 'translate-x-5' : 'translate-x-0'"
              />
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { API_BASE } from '../../config'

const userStore = useUserStore()

const categories = ref([])
const isLoading = ref(false)
const error = ref('')

function imgSrc(path) {
  return `${API_BASE}${path}`
}

function authHeaders() {
  return { 'Authorization': `tma ${userStore.initDataRaw || 'dev'}` }
}

async function fetchMenu() {
  if (!categories.value.length) isLoading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/menu`, { headers: authHeaders() })
    if (!res.ok) throw new Error('Не удалось загрузить меню')
    categories.value = await res.json()
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Ошибка загрузки меню'
  } finally {
    isLoading.value = false
  }
}

// --- Category form ---
const showCategoryForm = ref(false)
const categoryForm = reactive({ id: null, name: '', sort_order: 0 })
const categoryFile = ref(null)
const categoryPreview = ref('')
const categoryFileInput = ref(null)
const isSavingCategory = ref(false)
const categoryError = ref('')

function openCreateCategory() {
  categoryForm.id = null
  categoryForm.name = ''
  categoryForm.sort_order = categories.value.length
  categoryFile.value = null
  categoryPreview.value = ''
  categoryError.value = ''
  showCategoryForm.value = true
}

function openEditCategory(cat) {
  categoryForm.id = cat.id
  categoryForm.name = cat.name
  categoryForm.sort_order = cat.sort_order
  categoryFile.value = null
  categoryPreview.value = cat.image_url ? imgSrc(cat.image_url) : ''
  categoryError.value = ''
  showCategoryForm.value = true
}

function handleCategoryFileChange(e) {
  const file = e.target.files?.[0]
  if (file) {
    categoryFile.value = file
    categoryPreview.value = URL.createObjectURL(file)
  }
}

async function saveCategory() {
  categoryError.value = ''
  if (!categoryForm.name.trim()) return
  isSavingCategory.value = true

  try {
    const formData = new FormData()
    formData.append('name', categoryForm.name.trim())
    formData.append('sort_order', String(categoryForm.sort_order ?? 0))
    if (categoryFile.value) formData.append('image', categoryFile.value)

    const url = categoryForm.id
      ? `${API_BASE}/api/v1/admin/menu/categories/${categoryForm.id}`
      : `${API_BASE}/api/v1/admin/menu/categories`

    const res = await fetch(url, {
      method: categoryForm.id ? 'PATCH' : 'POST',
      headers: authHeaders(),
      body: formData
    })
    if (!res.ok) throw new Error('Не удалось сохранить категорию')

    showCategoryForm.value = false
    await fetchMenu()
  } catch (err) {
    console.error(err)
    categoryError.value = err.message || 'Ошибка сохранения'
  } finally {
    isSavingCategory.value = false
  }
}

// --- Item form ---
const showItemForm = ref(false)
const itemForm = reactive({ id: null, category_id: null, name: '', description: '', price: null, is_available: true })
const itemFile = ref(null)
const itemPreview = ref('')
const itemFileInput = ref(null)
const isSavingItem = ref(false)
const itemError = ref('')

function openCreateItem() {
  if (!categories.value.length) return
  itemForm.id = null
  itemForm.category_id = categories.value[0].id
  itemForm.name = ''
  itemForm.description = ''
  itemForm.price = null
  itemForm.is_available = true
  itemFile.value = null
  itemPreview.value = ''
  itemError.value = ''
  showItemForm.value = true
}

function openEditItem(item, categoryId) {
  itemForm.id = item.id
  itemForm.category_id = item.category_id ?? categoryId
  itemForm.name = item.name
  itemForm.description = item.description || ''
  itemForm.price = item.price
  itemForm.is_available = item.is_available
  itemFile.value = null
  itemPreview.value = item.image_url ? imgSrc(item.image_url) : ''
  itemError.value = ''
  showItemForm.value = true
}

function handleItemFileChange(e) {
  const file = e.target.files?.[0]
  if (file) {
    itemFile.value = file
    itemPreview.value = URL.createObjectURL(file)
  }
}

async function saveItem() {
  itemError.value = ''
  if (!itemForm.name.trim() || !itemForm.price) return
  isSavingItem.value = true

  try {
    const formData = new FormData()
    formData.append('name', itemForm.name.trim())
    formData.append('price', String(itemForm.price))
    formData.append('description', itemForm.description || '')
    formData.append('is_available', String(itemForm.is_available))
    if (itemForm.category_id != null) formData.append('category_id', String(itemForm.category_id))
    if (itemFile.value) formData.append('image', itemFile.value)

    const url = itemForm.id
      ? `${API_BASE}/api/v1/admin/menu/items/${itemForm.id}`
      : `${API_BASE}/api/v1/admin/menu/items`

    const res = await fetch(url, {
      method: itemForm.id ? 'PATCH' : 'POST',
      headers: authHeaders(),
      body: formData
    })
    if (!res.ok) throw new Error('Не удалось сохранить блюдо')

    showItemForm.value = false
    await fetchMenu()
  } catch (err) {
    console.error(err)
    itemError.value = err.message || 'Ошибка сохранения'
  } finally {
    isSavingItem.value = false
  }
}

async function toggleItem(item) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/menu/items/${item.id}/toggle`, {
      method: 'PATCH',
      headers: authHeaders()
    })
    if (!res.ok) throw new Error('Не удалось изменить доступность')
    const updated = await res.json()
    item.is_available = updated.is_available
  } catch (err) {
    console.error(err)
    alert(err.message)
  }
}

onMounted(() => {
  fetchMenu()
})
</script>
