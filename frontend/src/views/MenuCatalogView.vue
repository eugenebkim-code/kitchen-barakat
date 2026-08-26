<template>
  <div class="min-h-screen pb-28">
    <!-- Header / Banner -->
    <header class="bg-white/75 backdrop-blur-xl sticky top-0 z-30 shadow-sm shadow-black/5 border-b border-white/60">
      <div class="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <img src="/images/logo-barakat.png" alt="Barakat Cafe" class="w-10 h-10 rounded-full object-cover shadow-md shadow-emerald-900/20" />
          <div>
            <h1 class="font-extrabold text-zinc-900 text-lg leading-none tracking-tight">Кафе "БАРАКАТ"</h1>
            <p class="text-xs text-zinc-500 mt-0.5">традиционная узбекская кухня в городе Дунпо, Корея</p>
          </div>
        </div>

        <!-- Admin Dashboard Access Badge -->
        <button
          v-if="userStore.isAdmin"
          @click="$emit('open-admin')"
          class="px-3 py-1.5 bg-zinc-900 hover:bg-black text-amber-400 font-bold text-xs rounded-xl flex items-center gap-1.5 shadow-md shadow-zinc-900/20 active:scale-95 transition-all"
        >
          <span>⚙️ Админка</span>
        </button>

        <!-- Dev Mode Toggle (в браузере без Telegram) -->
        <button
          v-else-if="isDevBrowser"
          @click="toggleDevAdmin"
          class="px-2.5 py-1 bg-amber-100 hover:bg-amber-200 text-amber-800 font-bold text-[11px] rounded-xl flex items-center gap-1"
          title="Включить режим тестирования админки"
        >
          <span>🧪 Тест Админки</span>
        </button>
      </div>

      <!-- Kitchen Status Banner -->
      <div
        class="mx-4 mb-3 px-3.5 py-2 text-xs font-bold flex items-center justify-between rounded-xl border backdrop-blur-sm"
        :class="userStore.isOpen ? 'bg-emerald-50/90 text-emerald-800 border-emerald-200/70' : 'bg-red-50/90 text-red-800 border-red-200/70'"
      >
        <div class="flex items-center gap-2">
          <span class="relative flex h-2 w-2">
            <span
              class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
              :class="userStore.isOpen ? 'bg-emerald-400' : 'bg-red-400'"
            ></span>
            <span
              class="relative inline-flex rounded-full h-2 w-2"
              :class="userStore.isOpen ? 'bg-emerald-500' : 'bg-red-500'"
            ></span>
          </span>
          <span>{{ userStore.isOpen ? 'Кухня открыта • Принимаем заказы' : `Кухня закрыта • Приём заказов с ${userStore.openTime} до ${userStore.closeTime}` }}</span>
        </div>
        <span class="text-[10px] opacity-80 uppercase tracking-wider">KST (Корея)</span>
      </div>

      <!-- Category Photo Slider -->
      <div v-if="menuStore.categories.length > 0" class="flex overflow-x-auto px-4 pb-3 gap-3 no-scrollbar">
        <button
          v-for="cat in menuStore.categories"
          :key="cat.id"
          @click="menuStore.setActiveCategory(cat.id)"
          class="flex flex-col items-center gap-1.5 flex-shrink-0 w-16"
        >
          <div
            class="w-16 h-16 rounded-2xl overflow-hidden bg-zinc-100 flex items-center justify-center border-2 transition-all duration-200"
            :class="menuStore.activeCategoryId === cat.id ? 'border-amber-500 shadow-lg shadow-amber-500/30 scale-105' : 'border-white/70 shadow-sm'"
          >
            <img
              v-if="cat.image_url"
              :src="resolveImageUrl(cat.image_url)"
              :alt="cat.name"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-2xl">🍽️</span>
          </div>
          <span
            class="text-[11px] font-bold text-center leading-tight line-clamp-2"
            :class="menuStore.activeCategoryId === cat.id ? 'text-amber-600' : 'text-zinc-600'"
          >
            {{ cat.name }}
          </span>
        </button>
      </div>
    </header>

    <!-- Menu Items Grid -->
    <main class="max-w-lg mx-auto p-4">
      <div v-if="menuStore.isLoading" class="py-20 text-center space-y-3">
        <div class="animate-spin text-4xl drop-shadow-md">⏳</div>
        <p class="text-sm text-white font-bold drop-shadow-md">Загружаем вкусное меню...</p>
      </div>

      <div v-else-if="menuStore.error" class="py-12 text-center space-y-3">
        <p class="text-red-100 font-bold text-sm drop-shadow-md bg-red-600/80 backdrop-blur-sm inline-block px-4 py-2 rounded-xl">{{ menuStore.error }}</p>
        <button @click="menuStore.fetchMenu()" class="block mx-auto px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-amber-500/30 active:scale-95 transition-all">
          Повторить попытку
        </button>
      </div>

      <div v-else-if="currentCategoryItems.length === 0" class="py-12 text-center text-white font-semibold text-sm drop-shadow-md">
        В этой категории пока нет блюд
      </div>

      <div v-else class="grid grid-cols-2 gap-3.5">
        <MenuItemCard 
          v-for="dish in currentCategoryItems"
          :key="dish.id"
          :item="dish"
          :cartQuantity="getCartQuantity(dish.id)"
          @add="cartStore.addItem"
          @remove="cartStore.removeItem"
        />
      </div>

      <!-- Footer Credit -->
      <div class="mt-8 pb-4 text-center text-xs text-white/80 drop-shadow-md">
        Сделано командой
        <a
          href="https://mirae.team"
          target="_blank"
          rel="noopener noreferrer"
          class="font-bold text-amber-300 hover:text-amber-200 underline underline-offset-2"
        >
          Mirae Team
        </a>
        • Корея, 2026
      </div>
    </main>

    <!-- Floating Sticky Cart Bar Button -->
    <div v-if="cartStore.itemsCount > 0" class="fixed bottom-4 inset-x-4 max-w-lg mx-auto z-20">
      <button
        @click="isCartDrawerOpen = true"
        class="w-full py-3.5 px-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white rounded-2xl font-bold shadow-xl shadow-amber-900/30 ring-1 ring-white/20 flex items-center justify-between active:scale-[0.98] transition-all"
      >
        <div class="flex items-center gap-2.5">
          <span class="bg-white/20 px-2.5 py-1 rounded-xl text-xs">🛒 {{ cartStore.itemsCount }}</span>
          <span class="text-sm">Посмотреть корзину</span>
        </div>
        <span class="text-base font-extrabold">{{ cartStore.grandTotal.toLocaleString('ko-KR') }} ₩</span>
      </button>
    </div>

    <!-- Cart Drawer Component -->
    <CartDrawer 
      :isOpen="isCartDrawerOpen"
      @close="isCartDrawerOpen = false"
      @checkout="openCheckoutModal"
    />

    <!-- Checkout Modal Component -->
    <CheckoutModal 
      :isOpen="isCheckoutModalOpen"
      @close="isCheckoutModalOpen = false"
      @success="handleOrderSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useMenuStore } from '../stores/menu'
import { useCartStore } from '../stores/cart'
import { resolveImageUrl } from '../config'
import MenuItemCard from '../components/MenuItemCard.vue'
import CartDrawer from '../components/CartDrawer.vue'
import CheckoutModal from '../components/CheckoutModal.vue'

const emit = defineEmits(['open-admin', 'order-created'])

const userStore = useUserStore()
const menuStore = useMenuStore()
const cartStore = useCartStore()

const isCartDrawerOpen = ref(false)
const isCheckoutModalOpen = ref(false)

const isDevBrowser = computed(() => !window.Telegram?.WebApp?.initData)

function toggleDevAdmin() {
  userStore.isAdmin = !userStore.isAdmin
  if (userStore.isAdmin) {
    emit('open-admin')
  }
}

const currentCategoryItems = computed(() => {
  return menuStore.activeCategory?.items || []
})

function getCartQuantity(dishId) {
  const item = cartStore.items.find(i => i.id === dishId)
  return item ? item.quantity : 0
}

function openCheckoutModal() {
  if (!userStore.isOpen) {
    alert('Извините, кухня временно закрыта и не принимает заказы.')
    return
  }
  isCartDrawerOpen.value = false
  isCheckoutModalOpen.value = true
}

function handleOrderSuccess(orderId) {
  isCheckoutModalOpen.value = false
  emit('order-created', orderId)
}

onMounted(() => {
  menuStore.fetchMenu()
})
</script>
