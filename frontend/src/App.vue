<template>
  <div class="min-h-screen bg-zinc-50 font-sans antialiased text-zinc-900">
    <!-- Initial Loading Screen -->
    <div v-if="userStore.isLoading" class="min-h-screen flex flex-col items-center justify-center space-y-4">
      <div class="animate-spin text-5xl">🍳</div>
      <p class="text-sm font-bold text-zinc-600">Загрузка Kitchen WebApp...</p>
    </div>

    <template v-else>
      <!-- View Router Switcher -->
      <AdminDashboardView 
        v-if="currentView === 'admin' && userStore.isAdmin" 
        @close="currentView = 'catalog'" 
      />

      <OrderSuccessView 
        v-else-if="currentView === 'success'" 
        :orderId="createdOrderId" 
        @back-to-menu="currentView = 'catalog'" 
      />

      <MenuCatalogView 
        v-else 
        @open-admin="currentView = 'admin'" 
        @order-created="onOrderCreated" 
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from './stores/user'
import MenuCatalogView from './views/MenuCatalogView.vue'
import AdminDashboardView from './views/AdminDashboardView.vue'
import OrderSuccessView from './views/OrderSuccessView.vue'

const userStore = useUserStore()
const currentView = ref('catalog') // 'catalog' | 'admin' | 'success'
const createdOrderId = ref(null)

function onOrderCreated(orderId) {
  createdOrderId.value = orderId
  currentView.value = 'success'
}

onMounted(() => {
  userStore.initTelegramApp()
})
</script>
