import { defineStore } from 'pinia'
import { useUserStore } from './user'

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

        const response = await fetch('/api/v1/menu', { headers })
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
    },

    // Admin Action: Quick availability toggle
    async toggleItemAvailability(itemId) {
      const userStore = useUserStore()
      try {
        const headers = {
          'Authorization': `tma ${userStore.initDataRaw || 'dev'}`
        }

        const res = await fetch(`/api/v1/admin/menu/items/${itemId}/toggle`, {
          method: 'PATCH',
          headers
        })

        if (!res.ok) {
          throw new Error('Не удалось изменить статус блюда')
        }

        const updatedItem = await res.json()

        // Update local state immediately
        for (const cat of this.categories) {
          const item = cat.items.find(i => i.id === itemId)
          if (item) {
            item.is_available = updatedItem.is_available
            break
          }
        }
        return true
      } catch (err) {
        console.error('Failed toggle item availability:', err)
        alert(err.message)
        return false
      }
    }
  }
})
