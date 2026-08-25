<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="bg-white/95 backdrop-blur-xl w-full max-w-md rounded-3xl p-6 text-center space-y-6 shadow-2xl ring-1 ring-white/50">

      <!-- Icon & Status Badge -->
      <div class="relative inline-block">
        <div class="w-20 h-20 bg-gradient-to-br from-amber-400 to-amber-600 text-white rounded-3xl flex items-center justify-center text-4xl mx-auto shadow-lg shadow-amber-500/40">
          🎉
        </div>
        <span class="absolute -bottom-1 -right-1 bg-emerald-500 text-white rounded-full p-1 text-xs border-2 border-white shadow-sm">
          ✓
        </span>
      </div>

      <!-- Title & Details -->
      <div class="space-y-2">
        <h1 class="text-2xl font-extrabold text-zinc-900">Заказ успешно создан!</h1>
        <p class="text-xs text-amber-600 font-bold uppercase tracking-wider">
          Статус: На проверке администратора
        </p>
        <p class="text-xs text-zinc-500 leading-relaxed px-4">
          Мы уже получили ваш заказ и проверяем подтверждение оплаты. Скоро кухня приступит к приготовлению!
        </p>
      </div>

      <!-- Order Summary Card -->
      <div class="bg-zinc-50 rounded-2xl p-4 text-left border border-zinc-100 space-y-2 text-xs">
        <div class="flex justify-between text-zinc-500">
          <span>Номер заказа:</span>
          <span class="font-bold text-zinc-900 font-mono">#{{ orderId || '---' }}</span>
        </div>
        <div class="flex justify-between text-zinc-500">
          <span>Время создания:</span>
          <span class="font-semibold text-zinc-800">{{ formattedTime }}</span>
        </div>
      </div>

      <!-- Action Button -->
      <button
        @click="$emit('back-to-menu')"
        class="w-full py-3.5 bg-gradient-to-r from-zinc-900 to-zinc-800 hover:from-black hover:to-zinc-900 text-white font-bold rounded-2xl shadow-lg active:scale-95 transition-all text-sm"
      >
        Вернуться в меню
      </button>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  orderId: [Number, String]
})

defineEmits(['back-to-menu'])

const formattedTime = computed(() => {
  return new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
})
</script>
