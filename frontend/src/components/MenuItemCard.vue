<template>
  <div class="bg-white/95 backdrop-blur-sm rounded-3xl shadow-md shadow-black/5 border border-white/60 overflow-hidden flex flex-col justify-between h-full relative transition-all duration-300 hover:shadow-xl hover:shadow-amber-900/10 hover:-translate-y-1">
    <!-- Image -->
    <div class="relative w-full h-36 bg-zinc-100 overflow-hidden">
      <img
        v-if="item.image_url"
        :src="resolveImageUrl(item.image_url)"
        :alt="item.name"
        class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-zinc-400 text-3xl font-bold bg-gradient-to-br from-zinc-100 to-zinc-200">
        🍲
      </div>
      <div class="absolute inset-x-0 bottom-0 h-8 bg-gradient-to-t from-black/10 to-transparent pointer-events-none"></div>
    </div>

    <!-- Content -->
    <div class="p-3.5 flex-1 flex flex-col justify-between">
      <div>
        <h3 class="font-bold text-zinc-900 text-sm leading-tight line-clamp-1 mb-1">
          {{ localizeField(item, 'name', langStore.locale) }}
        </h3>
        <p v-if="item.description" class="text-xs text-zinc-500 line-clamp-3 mb-2 leading-relaxed">
          {{ localizeField(item, 'description', langStore.locale) }}
        </p>
      </div>

      <div class="mt-2 flex items-center justify-between gap-1.5">
        <span class="bg-gradient-to-r from-amber-600 to-amber-500 bg-clip-text text-transparent font-extrabold text-sm whitespace-nowrap">
          {{ item.price.toLocaleString('ko-KR') }} ₩
        </span>

        <!-- Quantity Counter / Add Button -->
        <div class="flex items-center">
          <div v-if="cartQuantity > 0" class="flex items-center bg-amber-50 rounded-xl border border-amber-200 p-0.5">
            <button
              @click="$emit('remove', item.id)"
              class="w-6 h-6 flex items-center justify-center rounded-lg bg-white text-amber-700 font-bold text-sm shadow-sm active:scale-95 transition-transform"
            >
              -
            </button>
            <span class="px-1.5 text-xs font-bold text-amber-900 min-w-[18px] text-center">
              {{ cartQuantity }}
            </span>
            <button
              @click="$emit('add', item)"
              class="w-6 h-6 flex items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-amber-600 text-white font-bold text-sm shadow-sm shadow-amber-500/40 active:scale-95 transition-transform"
            >
              +
            </button>
          </div>

          <button
            v-else
            @click="$emit('add', item)"
            class="px-2 py-1 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white font-bold text-[11px] rounded-lg shadow-md shadow-amber-500/30 active:scale-95 transition-all flex items-center gap-0.5 whitespace-nowrap"
          >
            <span>+</span>
            <span>{{ t('item.addToCart') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { resolveImageUrl } from '../config'
import { useI18n, localizeField } from '../i18n'

const { t, langStore } = useI18n()

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
