<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-bold text-zinc-900">Стоп-лист и Блюда</h2>
      <span class="text-xs text-zinc-500">Включение/Выключение в 1 клик</span>
    </div>

    <div v-if="menuStore.isLoading" class="text-center py-8 text-zinc-400 text-xs">
      Загрузка меню...
    </div>

    <div v-else class="space-y-3">
      <div 
        v-for="cat in menuStore.categories" 
        :key="cat.id" 
        class="bg-white rounded-2xl p-4 shadow-sm border border-zinc-100 space-y-3"
      >
        <h3 class="text-xs font-bold text-amber-600 uppercase tracking-wider border-b border-zinc-100 pb-2">
          {{ cat.name }}
        </h3>

        <div class="divide-y divide-zinc-100">
          <div 
            v-for="item in cat.items" 
            :key="item.id" 
            class="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-3"
          >
            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="font-bold text-sm text-zinc-900 truncate">{{ item.name }}</div>
              <div class="text-xs text-amber-600 font-semibold mt-0.5">
                {{ item.price.toLocaleString('ko-KR') }} ₩
              </div>
            </div>

            <!-- Availability Toggle Switch -->
            <button 
              @click="toggleItem(item.id)"
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
    </div>
  </div>
</template>

<script setup>
import { useMenuStore } from '../../stores/menu'

const menuStore = useMenuStore()

async function toggleItem(itemId) {
  await menuStore.toggleItemAvailability(itemId)
}
</script>
