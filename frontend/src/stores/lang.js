import { defineStore } from 'pinia'

const STORAGE_KEY = 'barakat_locale'

export const useLangStore = defineStore('lang', {
  state: () => ({
    locale: localStorage.getItem(STORAGE_KEY) || 'ru'
  }),

  actions: {
    setLocale(locale) {
      this.locale = locale
      localStorage.setItem(STORAGE_KEY, locale)
    }
  }
})
