import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { API_BASE } from '../config'

export const useMenuStore = defineStore('menu', {
  state: () => ({
    categories: [], // Array of { id, name, sort_order, items: [...] }
    activeCategoryId: null,
    isLoading: false,
    error: null,
  }),

  getters: {
    activeCategory: (state) => {
      if (!state.activeCategoryId && state.categories.length > 0) {
        return state.categories[0]
      }
      return state.categories.find(c => c.id === state.activeCategoryId) || state.categories[0] || null
    },

    allItems: (state) => {
      return state.categories.flatMap(c => c.items || [])
    }
  },

  actions: {
    async fetchMenu() {
      this.isLoading = true
      this.error = null

      try {
        const userStore = useUserStore()
        const headers = {}
        if (userStore.initDataRaw) {
          headers['Authorization'] = `tma ${userStore.initDataRaw}`
        }

        const response = await fetch(`${API_BASE}/api/v1/menu`, { headers })
        if (!response.ok) {
          throw new Error(`Failed to load menu: ${response.status}`)
        }

        const data = await response.json()
        this.categories = data

        if (data.length > 0 && !this.activeCategoryId) {
          this.activeCategoryId = data[0].id
        }
      } catch (err) {
        console.error('Error loading menu:', err)
        this.error = err.message || 'Не удалось загрузить меню'
      } finally {
        this.isLoading = false
      }
    },

    setActiveCategory(categoryId) {
      this.activeCategoryId = categoryId
    }
  }
})
