<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-bold text-zinc-900">Дашборд</h2>
      <button
        @click="fetchStats"
        class="text-xs bg-zinc-100 hover:bg-zinc-200 px-3 py-1.5 rounded-xl font-bold text-zinc-700"
      >
        🔄 Обновить
      </button>
    </div>

    <div v-if="isLoading && !loaded" class="text-center py-8 text-zinc-400 text-xs">
      Загрузка статистики...
    </div>

    <div v-else-if="error" class="bg-red-50 text-red-600 text-xs p-3 rounded-xl font-medium text-center">
      {{ error }}
    </div>

    <template v-else>
      <!-- Revenue cards -->
      <div class="grid grid-cols-3 gap-2.5">
        <div class="bg-white rounded-2xl p-3.5 shadow-sm border border-zinc-100 text-center space-y-1">
          <div class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">Сегодня</div>
          <div class="text-sm font-extrabold text-amber-600 leading-tight">
            {{ stats.sum_today.toLocaleString('ko-KR') }} ₩
          </div>
        </div>
        <div class="bg-white rounded-2xl p-3.5 shadow-sm border border-zinc-100 text-center space-y-1">
          <div class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">Неделя</div>
          <div class="text-sm font-extrabold text-amber-600 leading-tight">
            {{ stats.sum_week.toLocaleString('ko-KR') }} ₩
          </div>
        </div>
        <div class="bg-white rounded-2xl p-3.5 shadow-sm border border-zinc-100 text-center space-y-1">
          <div class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">Месяц</div>
          <div class="text-sm font-extrabold text-amber-600 leading-tight">
            {{ stats.sum_month.toLocaleString('ko-KR') }} ₩
          </div>
        </div>
      </div>

      <!-- Status count cards -->
      <div class="grid grid-cols-3 gap-2.5">
        <div class="bg-white rounded-2xl p-3.5 shadow-sm border border-zinc-100 text-center space-y-1">
          <div class="flex items-center justify-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">Принято</span>
          </div>
          <div class="text-xl font-extrabold text-emerald-600 leading-tight">{{ stats.count_accepted }}</div>
        </div>
        <div class="bg-white rounded-2xl p-3.5 shadow-sm border border-zinc-100 text-center space-y-1">
          <div class="flex items-center justify-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-red-500"></span>
            <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">Отклонено</span>
          </div>
          <div class="text-xl font-extrabold text-red-600 leading-tight">{{ stats.count_rejected }}</div>
        </div>
        <div class="bg-white rounded-2xl p-3.5 shadow-sm border border-zinc-100 text-center space-y-1">
          <div class="flex items-center justify-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-amber-400"></span>
            <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">Не обработано</span>
          </div>
          <div class="text-xl font-extrabold text-amber-600 leading-tight">{{ stats.count_pending }}</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { API_BASE } from '../../config'

const userStore = useUserStore()

const isLoading = ref(false)
const loaded = ref(false)
const error = ref('')

const stats = reactive({
  sum_today: 0,
  sum_week: 0,
  sum_month: 0,
  count_accepted: 0,
  count_rejected: 0,
  count_pending: 0
})

async function fetchStats() {
  isLoading.value = true
  error.value = ''

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/dashboard`, {
      headers: { 'Authorization': `tma ${userStore.initDataRaw || 'dev'}` }
    })
    if (!res.ok) throw new Error('Не удалось загрузить статистику')

    const data = await res.json()
    Object.assign(stats, data)
    loaded.value = true
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Ошибка загрузки'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>
