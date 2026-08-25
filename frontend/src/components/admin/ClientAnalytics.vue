<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-bold text-zinc-900">Клиенты и Аналитика</h2>
      <button 
        @click="fetchClients" 
        class="text-xs bg-zinc-100 hover:bg-zinc-200 px-3 py-1.5 rounded-xl font-bold text-zinc-700"
      >
        🔄 Обновить
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-8 text-zinc-400 text-xs">
      Загрузка списка клиентов...
    </div>

    <div v-else-if="error" class="bg-red-50 text-red-600 text-xs p-3 rounded-xl font-medium text-center">
      {{ error }}
    </div>

    <!-- Clients Cards -->
    <div v-else class="space-y-3">
      <div 
        v-for="client in sortedClients" 
        :key="client.id" 
        class="bg-white rounded-2xl p-4 shadow-sm border border-zinc-100 space-y-2 text-xs"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="font-bold text-sm text-zinc-900">
              {{ client.first_name || 'Без имени' }}
              <span v-if="client.username" class="text-zinc-400 font-normal">(@{{ client.username }})</span>
            </div>
            <div class="text-zinc-500 font-mono mt-0.5">{{ client.phone || 'Телефон не указан' }}</div>
          </div>
          <span class="px-2 py-0.5 bg-amber-100 text-amber-800 font-extrabold rounded-lg">
            {{ client.total_orders }} зак.
          </span>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-zinc-100 text-zinc-600">
          <span>Сумма LTV:</span>
          <span class="font-extrabold text-amber-600 text-sm">
            {{ client.ltv.toLocaleString('ko-KR') }} ₩
          </span>
        </div>

        <div v-if="client.last_active" class="text-[10px] text-zinc-400 text-right">
          Активность: {{ formatDate(client.last_active) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const clients = ref([])
const isLoading = ref(false)
const error = ref('')

const sortedClients = computed(() => {
  return [...clients.value].sort((a, b) => b.ltv - a.ltv)
})

async function fetchClients() {
  isLoading.value = true
  error.value = ''

  try {
    const res = await fetch('/api/v1/admin/clients', {
      headers: {
        'Authorization': `tma ${userStore.initDataRaw || 'dev'}`
      }
    })

    if (!res.ok) {
      throw new Error('Ошибка при загрузке аналитики клиентов')
    }

    clients.value = await res.json()
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Не удалось загрузить данные'
  } finally {
    isLoading.value = false
  }
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchClients()
})
</script>
