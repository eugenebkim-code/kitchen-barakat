<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition
      enter-active-class="transition opacity-0 ease-out duration-300"
      enter-to-class="opacity-100"
      leave-active-class="transition opacity-100 ease-in duration-200"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="isOpen" 
        @click="$emit('close')" 
        class="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
      ></div>
    </Transition>

    <!-- Sliding Drawer -->
    <Transition
      enter-active-class="transition transform ease-out duration-300"
      enter-from-class="translate-y-full"
      enter-to-class="translate-y-0"
      leave-active-class="transition transform ease-in duration-200"
      leave-from-class="translate-y-0"
      leave-to-class="translate-y-full"
    >
      <div
        v-if="isOpen"
        class="fixed inset-x-0 bottom-0 z-50 bg-white/95 backdrop-blur-xl rounded-t-3xl max-h-[85vh] flex flex-col shadow-2xl ring-1 ring-white/40 overflow-hidden"
      >
        <!-- Header -->
        <div class="p-4 border-b border-zinc-100 flex items-center justify-between bg-gradient-to-r from-amber-50/70 to-transparent">
          <div class="flex items-center gap-2">
            <span class="text-xl">🛒</span>
            <h2 class="text-lg font-bold text-zinc-900">Ваша корзина</h2>
            <span class="bg-amber-100 text-amber-800 text-xs font-bold px-2 py-0.5 rounded-full">
              {{ cartStore.itemsCount }} шт
            </span>
          </div>
          <button 
            @click="$emit('close')" 
            class="w-8 h-8 rounded-full bg-zinc-100 text-zinc-500 font-bold flex items-center justify-center hover:bg-zinc-200"
          >
            ✕
          </button>
        </div>

        <!-- Order Items List -->
        <div class="p-4 overflow-y-auto flex-1 space-y-3 divide-y divide-zinc-100">
          <div 
            v-for="item in cartStore.items" 
            :key="item.id" 
            class="pt-3 first:pt-0 flex items-center justify-between gap-3"
          >
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <img
                v-if="item.image_url"
                :src="resolveImageUrl(item.image_url)"
                class="w-12 h-12 rounded-xl object-cover bg-zinc-100 flex-shrink-0"
              />
              <div class="min-w-0">
                <h4 class="font-bold text-zinc-900 text-sm truncate">{{ item.name }}</h4>
                <div class="text-xs text-amber-600 font-semibold mt-0.5">
                  {{ (item.price * item.quantity).toLocaleString('ko-KR') }} ₩
                </div>
              </div>
            </div>

            <!-- Controls -->
            <div class="flex items-center bg-zinc-100 rounded-xl p-1 gap-1">
              <button 
                @click="cartStore.removeItem(item.id)" 
                class="w-7 h-7 bg-white rounded-lg flex items-center justify-center font-bold text-zinc-700 shadow-sm active:scale-95"
              >
                -
              </button>
              <span class="px-2 font-bold text-sm text-zinc-800">{{ item.quantity }}</span>
              <button 
                @click="cartStore.addItem(item)" 
                class="w-7 h-7 bg-amber-500 text-white rounded-lg flex items-center justify-center font-bold shadow-sm active:scale-95"
              >
                +
              </button>
            </div>
          </div>
        </div>

        <!-- Bottom Summary & Checkout Button -->
        <div class="p-4 bg-zinc-50 border-t border-zinc-100 space-y-3">
          <div class="space-y-1.5 text-sm">
            <div class="flex justify-between text-zinc-600">
              <span>Стоимость блюд:</span>
              <span class="font-semibold text-zinc-900">{{ cartStore.itemsTotal.toLocaleString('ko-KR') }} ₩</span>
            </div>
            <div class="flex justify-between text-zinc-600">
              <span>Доставка:</span>
              <span class="font-semibold text-zinc-900">
                {{ cartStore.deliveryType === 'pickup' ? 'Бесплатно (Самовывоз)' : `${cartStore.currentDeliveryFee.toLocaleString('ko-KR')} ₩` }}
              </span>
            </div>
            <div class="flex justify-between text-base font-extrabold text-zinc-900 pt-1 border-t border-zinc-200">
              <span>Итого:</span>
              <span class="text-amber-600">{{ cartStore.grandTotal.toLocaleString('ko-KR') }} ₩</span>
            </div>
          </div>

          <button
            @click="$emit('checkout')"
            class="w-full py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white font-bold rounded-2xl shadow-lg shadow-amber-500/30 active:scale-[0.98] transition-all flex items-center justify-center gap-2"
          >
            <span>Перейти к оформлению</span>
            <span>➔</span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useCartStore } from '../stores/cart'
import { resolveImageUrl } from '../config'

defineProps({
  isOpen: Boolean
})

defineEmits(['close', 'checkout'])

const cartStore = useCartStore()
</script>
