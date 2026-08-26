import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [], // Array of { id, name, price, quantity, image_url }
    deliveryType: 'delivery', // 'delivery' | 'pickup'
  }),

  getters: {
    itemsCount: (state) => {
      return state.items.reduce((sum, item) => sum + item.quantity, 0)
    },

    itemsTotal: (state) => {
      return state.items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    },

    currentDeliveryFee: (state) => {
      if (state.deliveryType === 'pickup') return 0
      const userStore = useUserStore()
      return userStore.deliveryFee || 3000
    },

    grandTotal(state) {
      return this.itemsTotal + this.currentDeliveryFee
    },

    isCartEmpty: (state) => state.items.length === 0
  },

  actions: {
    addItem(dish) {
      const existing = this.items.find(item => item.id === dish.id)
      if (existing) {
        existing.quantity++
      } else {
        this.items.push({
          id: dish.id,
          name: dish.name,
          name_ko: dish.name_ko,
          price: dish.price,
          quantity: 1,
          image_url: dish.image_url
        })
      }
    },

    removeItem(dishId) {
      const index = this.items.findIndex(item => item.id === dishId)
      if (index !== -1) {
        if (this.items[index].quantity > 1) {
          this.items[index].quantity--
        } else {
          this.items.splice(index, 1)
        }
      }
    },

    clearItemCompletely(dishId) {
      this.items = this.items.filter(item => item.id !== dishId)
    },

    setDeliveryType(type) {
      this.deliveryType = type
    },

    clearCart() {
      this.items = []
    }
  }
})
