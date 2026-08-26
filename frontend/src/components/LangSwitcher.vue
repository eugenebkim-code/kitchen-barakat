<template>
  <div class="fixed top-3 right-3 z-50 flex items-center bg-white/85 backdrop-blur-md rounded-full shadow-md shadow-black/10 border border-white/60 p-0.5 text-[11px] font-bold">
    <button
      type="button"
      @click="langStore.setLocale('ru')"
      class="px-2.5 py-1 rounded-full transition-all"
      :class="langStore.locale === 'ru' ? 'bg-zinc-900 text-white shadow-sm' : 'text-zinc-500'"
    >
      RU
    </button>
    <button
      type="button"
      @click="langStore.setLocale('ko')"
      class="px-2.5 py-1 rounded-full transition-all"
      :class="langStore.locale === 'ko' ? 'bg-zinc-900 text-white shadow-sm' : 'text-zinc-500'"
    >
      한글
    </button>
  </div>
</template>

<script setup>
import { useLangStore } from '../stores/lang'

const langStore = useLangStore()
</script>
