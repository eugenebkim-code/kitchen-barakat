<template>
  <div class="bg-white rounded-2xl shadow-sm border border-zinc-100 overflow-hidden flex flex-col justify-between h-full relative">
    <!-- Image -->
    <div class="relative w-full h-36 bg-zinc-100 overflow-hidden">
      <img
        v-if="item.image_url"
        :src="resolveImageUrl(item.image_url)"
        :alt="item.name"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-zinc-400 text-3xl font-bold bg-zinc-200">
        🍲
      </div>
    </div>

    <!-- Content -->
    <div class="p-3.5 flex-1 flex flex-col justify-between">
      <div>
        <h3 class="font-bold text-zinc-900 text-sm leading-tight line-clamp-1 mb-1">
          {{ item.name }}
        </h3>
        <p v-if="item.description" class="text-xs text-zinc-500 line-clamp-3 mb-2 leading-relaxed">
          {{ item.description }}
        </p>
      </div>

      <div class="mt-2 flex items-center justify-between">
        <span class="text-amber-600 font-extrabold text-base">
          {{ item.price.toLocaleString('ko-KR') }} ₩
        </span>

        <!-- Quantity Counter / Add Button -->
        <div class="flex items-center">
          <div v-if="cartQuantity > 0" class="flex items-center bg-amber-50 rounded-xl border border-amber-200 p-0.5">
            <button
              @click="$emit('remove', item.id)"
              class="w-7 h-7 flex items-center justify-center rounded-lg bg-white text-amber-700 font-bold shadow-sm active:scale-95 transition-transform"
            >
              -
            </button>
            <span class="px-2 text-sm font-bold text-amber-900 min-w-[20px] text-center">
              {{ cartQuantity }}
            </span>
            <button
              @click="$emit('add', item)"
              class="w-7 h-7 flex items-center justify-center rounded-lg bg-amber-500 text-white font-bold shadow-sm active:scale-95 transition-transform"
            >
              +
            </button>
          </div>

          <button
            v-else
            @click="$emit('add', item)"
            class="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs rounded-xl shadow-sm active:scale-95 transition-transform flex items-center gap-1"
          >
            <span>+</span>
            <span>В корзину</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { resolveImageUrl } from '../config'

defineProps({
  item: {
    type: Object,
    required: true
  },
  cartQuantity: {
    type: Number,
    default: 0
  }
})

defineEmits(['add', 'remove'])
</script>
