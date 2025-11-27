<template>
  <div class="p-2 bg-stone-200 h-full overflow-auto">
    <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4">
      <h2 class="text-lg font-bold text-stone-800 mb-4">
        {{ mode === 'add' ? 'Add New Business Partner' : 'Edit Business Partner' }}
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Basic Information -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Basic Information</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Partner Code *</label>
              <input v-model="formData.partner_code" :disabled="mode === 'edit'" type="text" required maxlength="20" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Partner Type *</label>
              <select v-model="formData.partner_type" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="VENDOR">Vendor</option>
                <option value="CUSTOMER">Customer</option>
                <option value="BOTH">Both</option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">Partner Name *</label>
              <input v-model="formData.partner_name" type="text" required maxlength="200" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Legal Information (Sensitive) -->
        <fieldset class="border-2 border-red-600 p-3 bg-red-50">
          <legend class="text-sm font-bold text-red-700 px-2">📋 Legal Information (Sensitive)</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Tax ID *</label>
              <input v-model="formData.tax_id" type="text" required maxlength="13" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Business Reg. No.</label>
              <input v-model="formData.business_registration_number" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Contact Information -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Contact Information</legend>
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">Address</label>
              <input v-model="formData.address" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">City</label>
              <input v-model="formData.city" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Province/State</label>
              <input v-model="formData.province" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Postal Code</label>
              <input v-model="formData.postal_code" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Country</label>
              <select v-model="formData.country" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="Thailand">Thailand</option>
                <option value="USA">USA</option>
                <option value="China">China</option>
                <option value="Japan">Japan</option>
                <option value="Singapore">Singapore</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Phone *</label>
              <input v-model="formData.phone" type="tel" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Email *</label>
              <input v-model="formData.email" type="email" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Financial Information (Highly Sensitive) -->
        <fieldset class="border-2 border-red-700 p-3 bg-red-100">
          <legend class="text-sm font-bold text-red-800 px-2">💳 Financial Information (Highly Sensitive)</legend>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Credit Limit (THB)</label>
              <input v-model.number="formData.credit_limit" type="number" step="0.01" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Payment Terms</label>
              <select v-model="formData.payment_terms" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="COD">COD (Cash on Delivery)</option>
                <option value="Net 7">Net 7</option>
                <option value="Net 15">Net 15</option>
                <option value="Net 30">Net 30</option>
                <option value="Net 60">Net 60</option>
                <option value="Net 90">Net 90</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Currency</label>
              <select v-model="formData.currency" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="THB">THB (Thai Baht)</option>
                <option value="USD">USD (US Dollar)</option>
                <option value="EUR">EUR (Euro)</option>
                <option value="CNY">CNY (Chinese Yuan)</option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">Bank Name</label>
              <input v-model="formData.bank_name" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Bank Account No.</label>
              <input v-model="formData.bank_account_number" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Contact Persons (Sensitive) -->
        <fieldset class="border-2 border-amber-600 p-3 bg-amber-50">
          <legend class="text-sm font-bold text-amber-800 px-2">👤 Contact Persons (Sensitive)</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Primary Contact Name</label>
              <input v-model="formData.primary_contact_name" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Primary Contact Phone</label>
              <input v-model="formData.primary_contact_phone" type="tel" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">Primary Contact Email</label>
              <input v-model="formData.primary_contact_email" type="email" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Status -->
        <div class="flex items-center gap-2">
          <input v-model="formData.is_active" type="checkbox" id="partner-active" class="w-4 h-4" />
          <label for="partner-active" class="text-sm font-bold text-stone-700">Active</label>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-4 border-t-2 border-stone-500">
          <button type="button" @click="$emit('cancel')" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
            Cancel
          </button>
          <button type="submit" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
            {{ mode === 'add' ? 'Create' : 'Update' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (value) => ['add', 'edit'].includes(value)
  },
  partner: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formData = ref({
  partner_code: '',
  partner_name: '',
  partner_type: 'VENDOR',
  tax_id: '',
  business_registration_number: '',
  address: '',
  city: '',
  province: '',
  postal_code: '',
  country: 'Thailand',
  phone: '',
  email: '',
  credit_limit: 0,
  payment_terms: 'Net 30',
  currency: 'THB',
  bank_name: '',
  bank_account_number: '',
  primary_contact_name: '',
  primary_contact_phone: '',
  primary_contact_email: '',
  is_active: true
})

// Load existing data in edit mode
watch(() => props.partner, (newPartner) => {
  if (newPartner && props.mode === 'edit') {
    formData.value = { ...newPartner._raw }
  }
}, { immediate: true })

function handleSubmit() {
  // Sanitize data: convert empty strings to null for optional fields
  const payload = { ...formData.value }
  
  const optionalFields = [
    'tax_id', 'business_registration_number', 'address', 'city', 'province', 'postal_code',
    'bank_name', 'bank_account_number', 
    'primary_contact_name', 'primary_contact_phone', 'primary_contact_email'
  ]
  
  optionalFields.forEach(field => {
    if (payload[field] === '') {
      payload[field] = null
    }
  })

  emit('submit', payload)
}
</script>
