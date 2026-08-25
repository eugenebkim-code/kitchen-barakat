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
      <div class="flex overflow-x-auto no-scrollbar border-t border-zinc-800 bg-zinc-900/90 text-xs font-bold px-2 pt-1">
        <button
          @click="activeTab = 'dashboard'"
          class="flex-shrink-0 px-3 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1 whitespace-nowrap"
          :class="activeTab === 'dashboard' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>📊 Дашборд</span>
        </button>
        <button
          @click="activeTab = 'orders'"
          class="flex-shrink-0 px-3 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1 whitespace-nowrap"
          :class="activeTab === 'orders' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>📦 Заказы</span>
        </button>
        <button
          @click="activeTab = 'menu'"
          class="flex-shrink-0 px-3 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1 whitespace-nowrap"
          :class="activeTab === 'menu' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>🍽️ Управление меню</span>
        </button>
        <button
          @click="activeTab = 'clients'"
          class="flex-shrink-0 px-3 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1 whitespace-nowrap"
          :class="activeTab === 'clients' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>👥 Клиенты</span>
        </button>
        <button
          @click="activeTab = 'broadcast'"
          class="flex-shrink-0 px-3 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1 whitespace-nowrap"
          :class="activeTab === 'broadcast' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>📢 Рассылка</span>
        </button>
        <button
          @click="activeTab = 'hours'"
          class="flex-shrink-0 px-3 py-2.5 text-center border-b-2 transition-all flex items-center justify-center gap-1 whitespace-nowrap"
          :class="activeTab === 'hours' ? 'border-amber-400 text-amber-400' : 'border-transparent text-zinc-400'"
        >
          <span>🕐 Время</span>
        </button>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="max-w-lg mx-auto p-4">
      <DashboardManager v-if="activeTab === 'dashboard'" />
      <OrdersManager v-else-if="activeTab === 'orders'" />
      <MenuManager v-else-if="activeTab === 'menu'" />
      <ClientAnalytics v-else-if="activeTab === 'clients'" />
      <BroadcastSender v-else-if="activeTab === 'broadcast'" />
      <WorkingHoursManager v-else-if="activeTab === 'hours'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DashboardManager from '../components/admin/DashboardManager.vue'
import OrdersManager from '../components/admin/OrdersManager.vue'
import MenuManager from '../components/admin/MenuManager.vue'
import ClientAnalytics from '../components/admin/ClientAnalytics.vue'
import BroadcastSender from '../components/admin/BroadcastSender.vue'
import WorkingHoursManager from '../components/admin/WorkingHoursManager.vue'

defineEmits(['close'])

const activeTab = ref('dashboard')
</script>
