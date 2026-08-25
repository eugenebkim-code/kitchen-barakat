<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-bold text-zinc-900">Рабочее время</h2>
      <button
        @click="fetchSchedule"
        class="text-xs bg-zinc-100 hover:bg-zinc-200 px-3 py-1.5 rounded-xl font-bold text-zinc-700"
      >
        🔄 Обновить
      </button>
    </div>

    <div v-if="isLoading && !loaded" class="text-center py-8 text-zinc-400 text-xs">
      Загрузка...
    </div>

    <div v-else class="bg-white rounded-2xl p-4 shadow-sm border border-zinc-100 space-y-4">
      <!-- Manual toggle -->
      <div class="flex items-center justify-between">
        <div>
          <div class="font-bold text-sm text-zinc-900">Кухня открыта</div>
          <div class="text-xs text-zinc-400 mt-0.5">
            {{ form.is_open_override ? 'Приём заказов включён (по расписанию)' : 'Принудительно закрыто' }}
          </div>
        </div>
        <button
          @click="form.is_open_override = !form.is_open_override"
          class="relative inline-flex h-7 w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
          :class="form.is_open_override ? 'bg-emerald-500' : 'bg-red-400'"
        >
          <span
            class="pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
            :class="form.is_open_override ? 'translate-x-5' : 'translate-x-0'"
          />
        </button>
      </div>

      <!-- Schedule -->
      <div class="grid grid-cols-2 gap-3 pt-2 border-t border-zinc-100">
        <div>
          <label class="block text-xs font-bold text-zinc-700 uppercase tracking-wider mb-1">Открытие</label>
          <input
            v-model="form.open_time"
            type="time"
            class="w-full px-3 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-zinc-700 uppercase tracking-wider mb-1">Закрытие</label>
          <input
            v-model="form.close_time"
            type="time"
            class="w-full px-3 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
      </div>

      <p class="text-xs text-zinc-400">
        Вне этих часов кухня автоматически считается закрытой, даже если тумблер выше включён.
      </p>

      <div class="flex items-center gap-2 pt-1">
        <span
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold"
          :class="currentIsOpen ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
        >
          <span class="w-2 h-2 rounded-full" :class="currentIsOpen ? 'bg-emerald-500' : 'bg-red-500'"></span>
          Сейчас: {{ currentIsOpen ? 'Открыто' : 'Закрыто' }}
        </span>
      </div>

      <p v-if="error" class="text-xs text-red-600 font-bold">{{ error }}</p>

      <button
        @click="saveSchedule"
        :disabled="isSaving"
        class="w-full py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-zinc-300 text-white font-bold text-sm rounded-xl active:scale-[0.98] transition-all"
      >
        {{ isSaving ? 'Сохранение...' : 'Сохранить' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { API_BASE } from '../../config'

const userStore = useUserStore()

const isLoading = ref(false)
const isSaving = ref(false)
const loaded = ref(false)
const error = ref('')
const currentIsOpen = ref(true)

const form = reactive({
  is_open_override: true,
  open_time: '11:00',
  close_time: '23:00'
})

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `tma ${userStore.initDataRaw || 'dev'}`
  }
}

async function fetchSchedule() {
  isLoading.value = true
  error.value = ''

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/settings/schedule`, { headers: authHeaders() })
    if (!res.ok) throw new Error('Не удалось загрузить расписание')

    const data = await res.json()
    form.is_open_override = data.is_open_override
    form.open_time = data.open_time
    form.close_time = data.close_time
    currentIsOpen.value = data.is_open
    loaded.value = true
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Ошибка загрузки'
  } finally {
    isLoading.value = false
  }
}

async function saveSchedule() {
  error.value = ''
  isSaving.value = true

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/settings/schedule`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: JSON.stringify({
        is_open_override: form.is_open_override,
        open_time: form.open_time,
        close_time: form.close_time
      })
    })
    if (!res.ok) throw new Error('Не удалось сохранить расписание')

    const data = await res.json()
    form.is_open_override = data.is_open_override
    form.open_time = data.open_time
    form.close_time = data.close_time
    currentIsOpen.value = data.is_open
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Ошибка сохранения'
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  fetchSchedule()
})
</script>
