<template>
  <div class="min-h-screen bg-zinc-50 pb-12">
    <!-- Admin Header -->
    <header class="bg-zinc-900 text-white sticky top-0 z-30 shadow-md">
      <div class="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-xl">👑</span>
          <div>
            <h1 class="font-extrabold text-sm leading-none text-amber-400">Панель Администратора</h1>
            <p class="text-[10px] text-zinc-400 mt-0.5">Управление кухней и клиентами</p>
          </div>
        </div>

        <button 
          @click="$emit('close')"
          class="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-bold text-xs rounded-lg active:scale-95 transition-all"
        >
          ✕ В меню
        </button>
      </div>

      <!-- Admin Tabs Navigation -->
      <div class="flex border-t border-zinc-800 bg-zinc-900/90 text-xs font-bold px-2 pt-1">
        <button
          @click="activeTab = 'orders'"
          class="flex-1 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1"
          :class="activeTab === 'orders' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>📦 Заказы</span>
        </button>
        <button
          @click="activeTab = 'stoplist'"
          class="flex-1 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1"
          :class="activeTab === 'stoplist' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>🛑 Стоп-лист</span>
        </button>
        <button 
          @click="activeTab = 'clients'"
          class="flex-1 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1"
          :class="activeTab === 'clients' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>👥 Клиенты</span>
        </button>
        <button 
          @click="activeTab = 'broadcast'"
          class="flex-1 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1"
          :class="activeTab === 'broadcast' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>📢 Рассылка</span>
        </button>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="max-w-lg mx-auto p-4">
      <OrdersManager v-if="activeTab === 'orders'" />
      <StopListManager v-else-if="activeTab === 'stoplist'" />
      <ClientAnalytics v-else-if="activeTab === 'clients'" />
      <BroadcastSender v-else-if="activeTab === 'broadcast'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import OrdersManager from '../components/admin/OrdersManager.vue'
import StopListManager from '../components/admin/StopListManager.vue'
import ClientAnalytics from '../components/admin/ClientAnalytics.vue'
import BroadcastSender from '../components/admin/BroadcastSender.vue'

defineEmits(['close'])

const activeTab = ref('orders')
</script>
