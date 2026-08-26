<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition opacity-0 duration-300"
      enter-to-class="opacity-100"
      leave-active-class="transition opacity-100 duration-200"
      leave-to-class="opacity-0"
    >
      <div v-if="isOpen" class="fixed inset-0 bg-black/70 z-50 overflow-y-auto flex items-end sm:items-center justify-center p-0 sm:p-4 backdrop-blur-sm">
        <div class="bg-white/95 backdrop-blur-xl w-full max-w-lg rounded-t-3xl sm:rounded-3xl max-h-[92vh] flex flex-col overflow-hidden shadow-2xl ring-1 ring-white/40">

          <!-- Modal Header -->
          <div class="p-4 border-b border-zinc-100 flex items-center justify-between bg-gradient-to-r from-amber-50/70 to-transparent">
            <div class="flex items-center gap-2">
              <h2 class="text-lg font-bold text-zinc-900">{{ t('checkout.title') }}</h2>
              <span class="relative inline-flex w-6 h-6">
                <span
                  v-if="!infoSeen"
                  class="absolute inset-0 rounded-full bg-amber-400 animate-ping"
                ></span>
                <button
                  type="button"
                  @click="toggleInfo"
                  :aria-label="t('checkout.infoAriaLabel')"
                  class="relative w-6 h-6 rounded-full flex items-center justify-center text-xs font-extrabold transition-colors"
                  :class="showInfo ? 'bg-amber-500 text-white' : 'bg-amber-100 text-amber-700 hover:bg-amber-200'"
                >
                  i
                </button>
              </span>
            </div>
            <button @click="$emit('close')" class="w-8 h-8 rounded-full bg-zinc-200 hover:bg-zinc-300 text-zinc-600 font-bold flex items-center justify-center transition-colors">
              ✕
            </button>
          </div>

          <div class="p-4 overflow-y-auto space-y-5 flex-1">
            <!-- Info: how to order -->
            <Transition
              enter-active-class="transition opacity-0 -translate-y-1 duration-200"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition opacity-100 duration-150"
              leave-to-class="opacity-0"
            >
              <div v-if="showInfo" class="bg-sky-50 border border-sky-200 rounded-2xl p-4 text-sm text-sky-900 space-y-2">
                <p class="font-bold text-sky-800">{{ t('checkout.infoTitle') }}</p>
                <ol class="list-decimal list-inside space-y-1.5 leading-snug">
                  <li>{{ t('checkout.infoStep1') }}</li>
                  <li>{{ t('checkout.infoStep2') }}</li>
                  <li>{{ t('checkout.infoStep3') }}</li>
                  <li>{{ t('checkout.infoStep4') }}</li>
                  <li>{{ t('checkout.infoStep5') }}</li>
                  <li>{{ t('checkout.infoStep6') }}</li>
                </ol>
              </div>
            </Transition>

            <!-- 1. Delivery / Pickup Switcher -->
            <div class="bg-zinc-100 p-1 rounded-2xl flex font-bold text-sm">
              <button 
                type="button"
                @click="setDeliveryType('delivery')" 
                class="flex-1 py-2.5 rounded-xl transition-all flex items-center justify-center gap-1.5"
                :class="form.deliveryType === 'delivery' ? 'bg-white text-amber-600 shadow-sm' : 'text-zinc-500'"
              >
                <span>{{ t('checkout.delivery') }}</span>
              </button>
              <button
                type="button"
                @click="setDeliveryType('pickup')"
                class="flex-1 py-2.5 rounded-xl transition-all flex items-center justify-center gap-1.5"
                :class="form.deliveryType === 'pickup' ? 'bg-white text-amber-600 shadow-sm' : 'text-zinc-500'"
              >
                <span>{{ t('checkout.pickup') }}</span>
              </button>
            </div>

            <!-- 2. Phone Input (Korean Format Validation) -->
            <div>
              <label class="block text-xs font-bold text-zinc-700 uppercase tracking-wider mb-1">
                {{ t('checkout.phoneLabel') }} <span class="text-red-500">*</span>
              </label>
              <input
                type="tel"
                v-model="form.phone"
                @input="formatKoreanPhone"
                :placeholder="t('checkout.phonePlaceholder')"
                maxlength="13"
                class="w-full px-4 py-3 bg-zinc-50 border rounded-xl text-zinc-900 font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all"
                :class="phoneError ? 'border-red-500 bg-red-50/30' : 'border-zinc-200'"
              />
              <p v-if="phoneError" class="text-xs text-red-500 mt-1 font-medium">{{ phoneError }}</p>
            </div>

            <!-- 3. Delivery Address Input -->
            <div v-if="form.deliveryType === 'delivery'">
              <label class="block text-xs font-bold text-zinc-700 uppercase tracking-wider mb-1">
                {{ t('checkout.addressLabel') }} <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="form.address"
                rows="2"
                :placeholder="t('checkout.addressPlaceholder')"
                class="w-full px-4 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all"
              ></textarea>
            </div>

            <!-- Comment -->
            <div>
              <label class="block text-xs font-bold text-zinc-700 uppercase tracking-wider mb-1">
                {{ t('checkout.commentLabel') }}
              </label>
              <input
                type="text"
                v-model="form.comment"
                :placeholder="t('checkout.commentPlaceholder')"
                class="w-full px-4 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all"
              />
            </div>

            <!-- 4. Bank Account Payment Details -->
            <div class="bg-gradient-to-br from-amber-50 to-amber-100/60 border border-amber-200/80 rounded-2xl p-4 space-y-3 shadow-sm">
              <div class="flex items-center justify-between border-b border-amber-200/50 pb-2">
                <span class="text-xs font-bold text-amber-900 uppercase">{{ t('checkout.requisitesTitle') }}</span>
                <span class="text-xs text-amber-700 font-medium">{{ t('checkout.bankTransfer') }}</span>
              </div>

              <div class="space-y-1 text-sm">
                <div class="flex justify-between">
                  <span class="text-zinc-600">{{ t('checkout.bank') }}</span>
                  <span class="font-bold text-zinc-900">{{ userStore.bankDetails.bank }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-zinc-600">{{ t('checkout.account') }}</span>
                  <div class="flex items-center gap-2">
                    <span class="font-extrabold text-zinc-900 font-mono">{{ userStore.bankDetails.account }}</span>
                    <button
                      type="button"
                      @click="copyAccount"
                      class="px-2 py-0.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white font-bold text-xs rounded-lg shadow-sm shadow-amber-500/30 active:scale-95 transition-all"
                    >
                      {{ isCopied ? t('checkout.copied') : t('checkout.copy') }}
                    </button>
                  </div>
                </div>
                <div class="flex justify-between">
                  <span class="text-zinc-600">{{ t('checkout.holder') }}</span>
                  <span class="font-bold text-zinc-900">{{ userStore.bankDetails.holder }}</span>
                </div>
                <div class="flex justify-between pt-2 border-t border-amber-200/50 text-base font-extrabold text-amber-900">
                  <span>{{ t('checkout.amountToPay') }}</span>
                  <span class="bg-gradient-to-r from-amber-600 to-amber-500 bg-clip-text text-transparent">{{ cartStore.grandTotal.toLocaleString('ko-KR') }} ₩</span>
                </div>
              </div>
            </div>

            <!-- 5. Payment Screenshot Upload -->
            <div>
              <label class="block text-xs font-bold text-zinc-700 uppercase tracking-wider mb-1">
                {{ t('checkout.receiptLabel') }} <span class="text-red-500">*</span>
              </label>

              <div 
                @click="triggerFileInput" 
                class="border-2 border-dashed rounded-2xl p-4 text-center cursor-pointer transition-colors relative overflow-hidden min-h-[110px] flex flex-col items-center justify-center"
                :class="receiptPreview ? 'border-amber-500 bg-amber-50/20' : 'border-zinc-300 hover:border-amber-400 bg-zinc-50'"
              >
                <input 
                  type="file" 
                  ref="fileInput" 
                  accept="image/*" 
                  @change="handleFileChange" 
                  class="hidden" 
                />

                <div v-if="receiptPreview" class="relative w-full flex items-center justify-between gap-3">
                  <img :src="receiptPreview" class="h-20 w-20 object-cover rounded-xl border border-zinc-200 shadow-sm" />
                  <div class="text-left flex-1 min-w-0">
                    <p class="text-xs font-bold text-zinc-900 truncate">{{ selectedFile?.name }}</p>
                    <p class="text-xs text-amber-600 font-semibold mt-0.5">{{ t('checkout.receiptUploaded') }}</p>
                    <p class="text-[11px] text-zinc-400 mt-1">{{ t('checkout.tapToReplace') }}</p>
                  </div>
                </div>

                <div v-else class="space-y-1">
                  <span class="text-2xl">📸</span>
                  <p class="text-xs font-bold text-zinc-700">{{ t('checkout.uploadReceipt') }}</p>
                  <p class="text-[11px] text-zinc-400">{{ t('checkout.fileHint') }}</p>
                </div>
              </div>
            </div>

            <!-- Submit Error -->
            <p v-if="submitError" class="text-xs text-red-600 font-bold text-center bg-red-50 p-2.5 rounded-xl border border-red-200">
              {{ submitError }}
            </p>
          </div>

          <!-- Actions -->
          <div class="p-4 bg-zinc-50 border-t border-zinc-100">
            <button
              @click="submitOrder"
              :disabled="isSubmitting"
              class="w-full py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 disabled:from-zinc-300 disabled:to-zinc-300 text-white font-bold rounded-2xl shadow-lg shadow-amber-500/30 active:scale-[0.98] transition-all flex items-center justify-center gap-2"
            >
              <span v-if="isSubmitting" class="animate-spin text-lg">⏳</span>
              <span>{{ isSubmitting ? t('checkout.sending') : t('checkout.submit') }}</span>
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useCartStore } from '../stores/cart'
import { API_BASE } from '../config'
import { useI18n } from '../i18n'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'success'])

const userStore = useUserStore()
const cartStore = useCartStore()
const { t } = useI18n()

const fileInput = ref(null)
const selectedFile = ref(null)
const receiptPreview = ref(null)
const isCopied = ref(false)
const isSubmitting = ref(false)
const showInfo = ref(false)
const infoSeen = ref(false)

function toggleInfo() {
  showInfo.value = !showInfo.value
  infoSeen.value = true
}
const submitError = ref('')
const phoneError = ref('')

const form = reactive({
  deliveryType: 'delivery',
  phone: '',
  address: '',
  comment: ''
})

onMounted(() => {
  form.deliveryType = userStore.lastDeliveryType || 'delivery'
  form.phone = userStore.formattedPhone || userStore.phone || ''
  form.address = userStore.savedAddress || ''
})

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    form.deliveryType = cartStore.deliveryType || 'delivery'
    if (!form.phone) form.phone = userStore.formattedPhone || userStore.phone || ''
    if (!form.address) form.address = userStore.savedAddress || ''
  }
})

function setDeliveryType(type) {
  form.deliveryType = type
  cartStore.setDeliveryType(type)
}

function formatKoreanPhone() {
  let value = form.phone.replace(/\D/g, '')
  if (value.length > 11) value = value.slice(0, 11)

  if (value.length > 7) {
    form.phone = `${value.slice(0, 3)}-${value.slice(3, 7)}-${value.slice(7)}`
  } else if (value.length > 3) {
    form.phone = `${value.slice(0, 3)}-${value.slice(3)}`
  } else {
    form.phone = value
  }
  
  validatePhone()
}

function validatePhone() {
  const cleaned = form.phone.replace(/\D/g, '')
  if (!cleaned) {
    phoneError.value = t('checkout.errorPhoneRequired')
    return false
  }
  if (!cleaned.startsWith('010') || cleaned.length !== 11) {
    phoneError.value = t('checkout.errorPhoneFormat')
    return false
  }
  phoneError.value = ''
  return true
}

function copyAccount() {
  navigator.clipboard.writeText(userStore.bankDetails.account)
  isCopied.value = true
  setTimeout(() => {
    isCopied.value = false
  }, 2000)
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (file) {
    selectedFile.value = file
    receiptPreview.value = URL.createObjectURL(file)
    submitError.value = ''
  }
}

async function submitOrder() {
  submitError.value = ''
  
  if (!validatePhone()) return

  if (form.deliveryType === 'delivery' && !form.address.trim()) {
    submitError.value = t('checkout.errorAddressRequired')
    return
  }

  if (!selectedFile.value) {
    submitError.value = t('checkout.errorReceiptRequired')
    return
  }

  isSubmitting.value = true

  try {
    const formData = new FormData()
    formData.append('order_type', form.deliveryType)
    formData.append('phone', form.phone)
    formData.append('address', form.address || '')
    formData.append('comment', form.comment || '')
    
    // Convert cart items payload
    const itemsPayload = cartStore.items.map(item => ({
      menu_item_id: item.id,
      quantity: item.quantity
    }))
    formData.append('items', JSON.stringify(itemsPayload))
    formData.append('receipt_image', selectedFile.value)

    const response = await fetch(`${API_BASE}/api/v1/orders`, {
      method: 'POST',
      headers: {
        'Authorization': `tma ${userStore.initDataRaw}`
      },
      body: formData
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || t('checkout.errorSubmitFailed'))
    }

    const result = await response.json()

    // Update user profile locally
    userStore.updateUserProfileLocally({
      phone: form.phone,
      address: form.address,
      deliveryType: form.deliveryType
    })

    cartStore.clearCart()
    emit('success', result.order_id)
  } catch (err) {
    console.error('Submit order error:', err)
    submitError.value = err.message || t('checkout.errorSubmitGeneric')
  } finally {
    isSubmitting.value = false
  }
}
</script>
