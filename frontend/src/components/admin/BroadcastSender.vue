<template>
  <div class="space-y-4 bg-white rounded-2xl p-4 shadow-sm border border-zinc-100">
    <div>
      <h2 class="text-base font-bold text-zinc-900">Рассылка клиентам</h2>
      <p class="text-xs text-zinc-500">Массовое сообщение во все чаты пользователей</p>
    </div>

    <!-- Form -->
    <div class="space-y-3">
      <div>
        <label class="block text-xs font-bold text-zinc-700 uppercase mb-1">
          Текст сообщения <span class="text-red-500">*</span>
        </label>
        <textarea 
          v-model="messageText"
          rows="4"
          placeholder="Внимание! Сегодня скидка 15% на все корейские сеты! 🥩"
          class="w-full px-3.5 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-xs text-zinc-900 focus:outline-none focus:ring-2 focus:ring-amber-500"
        ></textarea>
      </div>

      <div>
        <label class="block text-xs font-bold text-zinc-700 uppercase mb-1">
          URL картинки (опционально)
        </label>
        <input 
          type="url"
          v-model="imageUrl"
          placeholder="https://example.com/banner.jpg"
          class="w-full px-3.5 py-2 bg-zinc-50 border border-zinc-200 rounded-xl text-xs text-zinc-900 focus:outline-none focus:ring-2 focus:ring-amber-500"
        />
      </div>

      <!-- Preview image if provided -->
      <div v-if="imageUrl" class="relative rounded-xl overflow-hidden h-32 bg-zinc-100 border">
        <img :src="imageUrl" class="w-full h-full object-cover" @error="imageError = true" />
      </div>

      <!-- Action Buttons -->
      <div class="pt-2 flex items-center gap-2">
        <button 
          @click="sendTestBroadcast"
          :disabled="isSending || !messageText.trim()"
          class="flex-1 py-2.5 bg-zinc-100 hover:bg-zinc-200 disabled:opacity-50 text-zinc-800 font-bold text-xs rounded-xl transition-all"
        >
          🧪 Тест себе
        </button>
        <button 
          @click="startMassBroadcast"
          :disabled="isSending || !messageText.trim()"
          class="flex-1 py-2.5 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-md transition-all"
        >
          🚀 Запустить
        </button>
      </div>

      <!-- Feedback status -->
      <p v-if="statusMessage" class="text-xs font-bold text-center p-2 rounded-xl" :class="statusClass">
        {{ statusMessage }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import { API_BASE } from '../../config'

const userStore = useUserStore()

const messageText = ref('')
const imageUrl = ref('')
const isSending = ref(false)
const statusMessage = ref('')
const isSuccess = ref(false)

const statusClass = computed(() => {
  return isSuccess.value ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'
})

async function sendTestBroadcast() {
  statusMessage.value = ''
  isSending.value = true

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/broadcast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `tma ${userStore.initDataRaw || 'dev'}`
      },
      body: JSON.stringify({
        message_text: `[ТЕСТ] ${messageText.value}`,
        image_url: imageUrl.value || null,
        target_telegram_id: userStore.telegramId || 123456789
      })
    })

    if (!res.ok) throw new Error('Ошибка отправки тестовой рассылки')

    isSuccess.value = true
    statusMessage.value = 'Тестовое сообщение отправлено вам в Telegram!'
  } catch (err) {
    isSuccess.value = false
    statusMessage.value = err.message || 'Ошибка'
  } finally {
    isSending.value = false
  }
}

async function startMassBroadcast() {
  if (!confirm('Вы уверены, что хотите запустить массовую рассылку всем клиентам?')) return

  statusMessage.value = ''
  isSending.value = true

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/broadcast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `tma ${userStore.initDataRaw || 'dev'}`
      },
      body: JSON.stringify({
        message_text: messageText.value,
        image_url: imageUrl.value || null
      })
    })

    if (!res.ok) throw new Error('Ошибка запуска массовой рассылки')

    isSuccess.value = true
    statusMessage.value = 'Массовая рассылка успешно запущена в фоновом режиме!'
    messageText.value = ''
    imageUrl.value = ''
  } catch (err) {
    isSuccess.value = false
    statusMessage.value = err.message || 'Ошибка запуска'
  } finally {
    isSending.value = false
  }
}
</script>
