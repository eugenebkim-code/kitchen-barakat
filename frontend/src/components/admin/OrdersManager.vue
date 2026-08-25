<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-bold text-zinc-900">Заказы</h2>
      <button
        @click="fetchOrders"
        class="text-xs bg-zinc-100 hover:bg-zinc-200 px-3 py-1.5 rounded-xl font-bold text-zinc-700"
      >
        🔄 Обновить
      </button>
    </div>

    <div v-if="isLoading && !orders.length" class="text-center py-8 text-zinc-400 text-xs">
      Загрузка заказов...
    </div>

    <div v-else-if="error" class="bg-red-50 text-red-600 text-xs p-3 rounded-xl font-medium text-center">
      {{ error }}
    </div>

    <div v-else-if="!orders.length" class="text-center py-8 text-zinc-400 text-xs">
      Заказов пока нет
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="order in orders"
        :key="order.id"
        class="bg-white rounded-2xl p-4 shadow-sm border border-zinc-100 space-y-3 text-xs"
      >
        <!-- Header: id, dot, status, time -->
        <div class="flex items-start justify-between gap-2">
          <div class="flex items-center gap-2">
            <span
              class="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
              :class="dotClass(order)"
            ></span>
            <div>
              <div class="font-bold text-sm text-zinc-900">
                Заказ #{{ order.id }}
                <span class="text-zinc-400 font-normal">· {{ order.order_type === 'delivery' ? 'Доставка' : 'Самовывоз' }}</span>
              </div>
              <div class="text-zinc-400 text-[10px] mt-0.5">{{ formatDate(order.created_at) }}</div>
            </div>
          </div>
          <span class="px-2 py-0.5 bg-amber-100 text-amber-800 font-extrabold rounded-lg whitespace-nowrap">
            {{ order.total_amount.toLocaleString('ko-KR') }} ₩
          </span>
        </div>

        <!-- Contact / address -->
        <div class="text-zinc-600 space-y-0.5">
          <div class="font-mono">{{ order.phone }}</div>
          <div v-if="order.address">{{ order.address }}</div>
          <div v-if="order.comment" class="italic text-zinc-400">«{{ order.comment }}»</div>
        </div>

        <!-- Items -->
        <div class="border-t border-zinc-100 pt-2 space-y-1">
          <div v-for="item in order.items" :key="item.id" class="flex justify-between text-zinc-600">
            <span>{{ item.item_name }} x{{ item.quantity }}</span>
            <span>{{ (item.price * item.quantity).toLocaleString('ko-KR') }} ₩</span>
          </div>
        </div>

        <!-- Receipt link -->
        <a
          :href="`${API_BASE}${order.payment_screenshot_url}`"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-block text-amber-600 font-bold underline"
        >
          📎 Чек оплаты
        </a>

        <!-- Status control -->
        <div class="border-t border-zinc-100 pt-3 flex items-center justify-between gap-2">
          <span class="font-bold" :class="labelClass(order)">{{ statusLabel(order) }}</span>
          <select
            :value="order.status"
            @change="updateStatus(order, $event.target.value)"
            :disabled="updatingId === order.id"
            class="border border-zinc-200 rounded-lg px-2 py-1.5 text-xs font-bold text-zinc-700 bg-zinc-50"
          >
            <option v-for="opt in statusOptions(order)" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { API_BASE } from '../../config'

const userStore = useUserStore()
const orders = ref([])
const isLoading = ref(false)
const error = ref('')
const updatingId = ref(null)
let pollTimer = null

const STATUS_META = {
  pending: { label: 'Ожидает ответа', color: 'yellow' },
  accepted: { label: 'Принято', color: 'green' },
  cooking: { label: 'Готовится', color: 'green' },
  shipped: { label: 'В доставке', color: 'green' },
  rejected: { label: 'Отказано', color: 'red' },
  cancelled: { label: 'Отменено', color: 'red' },
}

const DOT_CLASSES = {
  green: 'bg-emerald-500',
  yellow: 'bg-amber-400',
  red: 'bg-red-500',
}

const LABEL_CLASSES = {
  green: 'text-emerald-600',
  yellow: 'text-amber-600',
  red: 'text-red-600',
}

function statusMeta(order) {
  const meta = STATUS_META[order.status] || STATUS_META.pending
  if (order.status === 'shipped' && order.order_type === 'pickup') {
    return { ...meta, label: 'Ожидает самовывоза' }
  }
  return meta
}

function statusLabel(order) {
  return statusMeta(order).label
}

function dotClass(order) {
  return DOT_CLASSES[statusMeta(order).color]
}

function labelClass(order) {
  return LABEL_CLASSES[statusMeta(order).color]
}

function statusOptions(order) {
  return Object.entries(STATUS_META).map(([value, meta]) => ({
    value,
    label: value === 'shipped' && order.order_type === 'pickup' ? 'Ожидает самовывоза' : meta.label,
  }))
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function fetchOrders() {
  if (!orders.value.length) isLoading.value = true
  error.value = ''

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/orders`, {
      headers: { 'Authorization': `tma ${userStore.initDataRaw || 'dev'}` }
    })

    if (!res.ok) {
      throw new Error('Ошибка при загрузке заказов')
    }

    orders.value = await res.json()
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Не удалось загрузить заказы'
  } finally {
    isLoading.value = false
  }
}

async function updateStatus(order, newStatus) {
  if (newStatus === order.status) return
  updatingId.value = order.id
  const previousStatus = order.status

  try {
    const res = await fetch(`${API_BASE}/api/v1/admin/orders/${order.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `tma ${userStore.initDataRaw || 'dev'}`
      },
      body: JSON.stringify({ status: newStatus })
    })

    if (!res.ok) {
      throw new Error('Не удалось изменить статус заказа')
    }

    const updated = await res.json()
    const idx = orders.value.findIndex(o => o.id === order.id)
    if (idx !== -1) orders.value[idx] = updated
  } catch (err) {
    console.error(err)
    order.status = previousStatus
    alert(err.message)
  } finally {
    updatingId.value = null
  }
}

onMounted(() => {
  fetchOrders()
  pollTimer = setInterval(fetchOrders, 15000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>
