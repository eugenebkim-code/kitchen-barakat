import { defineStore } from 'pinia'
import { API_BASE } from '../config'

export const useUserStore = defineStore('user', {
  state: () => ({
    tgUser: null,
    initDataRaw: '',
    id: null,
    telegramId: null,
    phone: '',
    savedAddress: '',
    lastDeliveryType: 'delivery',
    isAdmin: false,
    
    // Store Settings
    isOpen: true,
    deliveryFee: 3000,
    bankDetails: {
      bank: 'KB Kookmin Bank',
      account: '123-4567-890123',
      holder: 'KIM OWNER'
    },
    
    isLoading: false,
    error: null
  }),

  getters: {
    formattedPhone: (state) => {
      if (!state.phone) return ''
      const cleaned = state.phone.replace(/\D/g, '')
      if (cleaned.length === 11) {
        return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 7)}-${cleaned.slice(7)}`
      }
      return state.phone
    }
  },

  actions: {
    async initTelegramApp() {
      this.isLoading = true
      this.error = null

      try {
        const tg = window.Telegram?.WebApp
        if (tg) {
          tg.ready()
          tg.expand()
          this.initDataRaw = tg.initData || ''
          
          if (tg.initDataUnsafe?.user) {
            this.tgUser = tg.initDataUnsafe.user
            this.telegramId = tg.initDataUnsafe.user.id
          }
        }

        // Validate HMAC signature & fetch profile + settings from backend
        const response = await fetch(`${API_BASE}/api/v1/auth/telegram`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `tma ${this.initDataRaw}`
          }
        })

        if (!response.ok) {
          throw new Error(`Auth failed with status ${response.status}`)
        }

        const data = await response.json()
        
        // Save user profile state
        if (data.user) {
          this.id = data.user.id
          this.telegramId = data.user.telegram_id
          this.phone = data.user.phone || ''
          this.savedAddress = data.user.saved_address || ''
          this.lastDeliveryType = data.user.last_delivery_type || 'delivery'
          this.isAdmin = Boolean(data.user.is_admin)
        }

        // Save store settings
        if (data.settings) {
          this.isOpen = data.settings.is_open ?? true
          this.deliveryFee = data.settings.delivery_fee ?? 3000
          if (data.settings.bank_details) {
            this.bankDetails = data.settings.bank_details
          }
        }
      } catch (err) {
        console.error('Error in initTelegramApp:', err)
        this.error = err.message || 'Ошибка авторизации'
        
        // Fallback for standalone browser testing / dev mode
        if (!this.initDataRaw) {
          console.warn('Running in dev mode without Telegram initData')
        }
      } finally {
        this.isLoading = false
      }
    },

    updateUserProfileLocally({ phone, address, deliveryType }) {
      if (phone) this.phone = phone
      if (address !== undefined) this.savedAddress = address
      if (deliveryType) this.lastDeliveryType = deliveryType
    }
  }
})
