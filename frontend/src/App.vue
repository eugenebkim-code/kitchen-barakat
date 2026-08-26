<template>
  <!-- Fixed background photo, sits behind every view -->
  <div class="fixed inset-0 -z-10 overflow-hidden bg-zinc-900">
    <div class="absolute inset-0 bg-cover bg-center scale-105" style="background-image: url('/images/bg-city-other.png')"></div>
    <div class="absolute inset-0 bg-gradient-to-b from-zinc-900/65 via-zinc-900/45 to-zinc-900/55"></div>
  </div>

  <div class="min-h-screen font-sans antialiased text-zinc-900">
    <LangSwitcher v-if="currentView !== 'admin'" />

    <!-- Initial Loading Screen -->
    <div v-if="userStore.isLoading" class="min-h-screen flex flex-col items-center justify-center space-y-4">
      <div class="animate-spin text-5xl drop-shadow-lg">🍳</div>
      <p class="text-sm font-bold text-white drop-shadow-md">{{ t('app.loading') }}</p>
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
import { useI18n } from './i18n'
import MenuCatalogView from './views/MenuCatalogView.vue'
import AdminDashboardView from './views/AdminDashboardView.vue'
import OrderSuccessView from './views/OrderSuccessView.vue'
import LangSwitcher from './components/LangSwitcher.vue'

const userStore = useUserStore()
const { t } = useI18n()
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
