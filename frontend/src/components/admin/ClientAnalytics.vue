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
            <div class="flex items-center gap-1.5 mt-0.5">
              <span class="text-zinc-500 font-mono">{{ client.phone || 'Телефон не указан' }}</span>
              <button
                v-if="client.phone"
                @click="copyPhone(client)"
                class="px-1.5 py-0.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-600 font-bold rounded-lg text-[10px] active:scale-95 transition-transform"
              >
                {{ copiedId === client.id ? '✓ Скопировано' : '📋 Копировать' }}
              </button>
            </div>
          </div>
          <span class="px-2 py-0.5 bg-amber-100 text-amber-800 font-extrabold rounded-lg whitespace-nowrap">
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

        <!-- Personal message composer -->
        <div class="pt-2 border-t border-zinc-100">
          <button
            v-if="messagingId !== client.id"
            @click="openComposer(client)"
            class="text-amber-600 font-bold"
          >
            ✉️ Написать клиенту
          </button>

          <div v-else class="space-y-2">
            <textarea
              v-model="draft"
              rows="3"
              placeholder="Текст личного сообщения..."
              class="w-full px-3 py-2 bg-zinc-50 border border-zinc-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-amber-500"
            ></textarea>

            <p v-if="sendError" class="text-red-600 font-bold">{{ sendError }}</p>
            <p v-if="sendSuccess" class="text-emerald-600 font-bold">Сообщение отправлено!</p>

            <div class="flex items-center gap-2">
              <button
                @click="sendPersonalMessage(client)"
                :disabled="isSending || !draft.trim()"
                class="flex-1 py-2 bg-amber-500 hover:bg-amber-600 disabled:bg-zinc-300 text-white font-bold rounded-xl active:scale-[0.98] transition-all"
              >
                {{ isSending ? 'Отправка...' : 'Отправить' }}
              </button>
              <button
                @click="closeComposer"
                class="px-3 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-700 font-bold rounded-xl"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { API_BASE } from '../../config'

const userStore = useUserStore()
const clients = ref([])
const isLoading = ref(false)
const error = ref('')

const copiedId = ref(null)
const messagingId = ref(null)
const draft = ref('')
const isSending = ref(false)
const sendError = ref('')
const sendSuccess = ref(false)

const sortedClients = computed(() => {
  return [...clients.value].sort((a, b) => b.ltv - a.ltv)
})

async function fetchClients() {
  isLoading.value = true
  error.value = ''

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/clients`, {
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

async function copyPhone(client) {
  try {
    await navigator.clipboard.writeText(client.phone)
    copiedId.value = client.id
    setTimeout(() => {
      if (copiedId.value === client.id) copiedId.value = null
    }, 1500)
  } catch (err) {
    console.error('Clipboard write failed:', err)
  }
}

function openComposer(client) {
  messagingId.value = client.id
  draft.value = ''
  sendError.value = ''
  sendSuccess.value = false
}

function closeComposer() {
  messagingId.value = null
  draft.value = ''
  sendError.value = ''
  sendSuccess.value = false
}

async function sendPersonalMessage(client) {
  sendError.value = ''
  sendSuccess.value = false
  isSending.value = true

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/broadcast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `tma ${userStore.initDataRaw || 'dev'}`
      },
      body: JSON.stringify({
        message_text: draft.value,
        target_telegram_id: client.telegram_id
      })
    })

    if (!res.ok) throw new Error('Не удалось отправить сообщение')

    sendSuccess.value = true
    draft.value = ''
    setTimeout(() => {
      if (messagingId.value === client.id) closeComposer()
    }, 1500)
  } catch (err) {
    console.error(err)
    sendError.value = err.message || 'Ошибка отправки'
  } finally {
    isSending.value = false
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
