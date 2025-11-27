<template>
  <div class="p-2 bg-stone-200 h-full overflow-auto">
    <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4">
      <h2 class="text-lg font-bold text-stone-800 mb-4">
        {{ mode === 'add' ? 'Add New Warehouse' : 'Edit Warehouse' }}
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Basic Information -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Basic Information</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Warehouse Code *</label>
              <input v-model="formData.warehouse_code" :disabled="mode === 'edit'" type="text" required maxlength="20" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Warehouse Type</label>
              <select v-model="formData.warehouse_type" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="Main">Main Warehouse</option>
                <option value="Transit">Transit</option>
                <option value="Consignment">Consignment</option>
                <option value="3PL">3PL (Third Party)</option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">Warehouse Name *</label>
              <input v-model="formData.warehouse_name" type="text" required maxlength="200" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Location Information -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Location Information</legend>
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">Location/Address *</label>
              <input v-model="formData.location" type="text" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
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
                <option value="Vietnam">Vietnam</option>
                <option value="Malaysia">Malaysia</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Capacity Information (Sensitive) -->
        <fieldset class="border-2 border-amber-600 p-3 bg-amber-50">
          <legend class="text-sm font-bold text-amber-800 px-2">📦 Capacity Information (Sensitive)</legend>
          <div class="grid grid-cols-4 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Total Area (sq.m)</label>
              <input v-model.number="formData.total_area_sqm" type="number" step="0.01" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Storage Capacity (m³)</label>
              <input v-model.number="formData.storage_capacity_cbm" type="number" step="0.01" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Number of Zones</label>
              <input v-model.number="formData.number_of_zones" type="number" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Max Weight (tons)</label>
              <input v-model.number="formData.max_weight_capacity_tons" type="number" step="0.01" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Operational Information -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Operational Information</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Operating Hours</label>
              <input v-model="formData.operating_hours" type="text" placeholder="e.g., Mon-Fri 8:00-17:00" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Security Level</label>
              <select v-model="formData.security_level" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="Standard">Standard</option>
                <option value="High">High</option>
                <option value="Maximum">Maximum</option>
              </select>
            </div>
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-2">
                <input v-model="formData.temperature_controlled" type="checkbox" id="temp-controlled" class="w-4 h-4" />
                <label for="temp-controlled" class="text-xs font-bold text-stone-700">Temperature Controlled</label>
              </div>
              <div class="flex items-center gap-2">
                <input v-model="formData.hazmat_certified" type="checkbox" id="hazmat" class="w-4 h-4" />
                <label for="hazmat" class="text-xs font-bold text-stone-700">Hazmat Certified</label>
              </div>
            </div>
          </div>
        </fieldset>

        <!-- Management (Sensitive) -->
        <fieldset class="border-2 border-red-600 p-3 bg-red-50">
          <legend class="text-sm font-bold text-red-700 px-2">👤 Management (Sensitive)</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Manager Name</label>
              <input v-model="formData.manager_name" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Manager Phone</label>
              <input v-model="formData.manager_phone" type="tel" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Manager Email</label>
              <input v-model="formData.manager_email" type="email" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Monthly Operating Cost (THB)</label>
              <input v-model.number="formData.monthly_operating_cost" type="number" step="0.01" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Status -->
        <div class="flex items-center gap-2">
          <input v-model="formData.is_active" type="checkbox" id="warehouse-active" class="w-4 h-4" />
          <label for="warehouse-active" class="text-sm font-bold text-stone-700">Active</label>
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
  warehouse: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formData = ref({
  warehouse_code: '',
  warehouse_name: '',
  warehouse_type: 'Main',
  location: '',
  city: '',
  province: '',
  postal_code: '',
  country: 'Thailand',
  total_area_sqm: null,
  storage_capacity_cbm: null,
  number_of_zones: null,
  max_weight_capacity_tons: null,
  operating_hours: '',
  security_level: 'Standard',
  temperature_controlled: false,
  hazmat_certified: false,
  manager_name: '',
  manager_phone: '',
  manager_email: '',
  monthly_operating_cost: null,
  is_active: true
})

// Load existing data in edit mode
watch(() => props.warehouse, (newWarehouse) => {
  if (newWarehouse && props.mode === 'edit') {
    formData.value = { ...newWarehouse._raw }
  }
}, { immediate: true })

function handleSubmit() {
  // Sanitize data: convert empty strings to null for optional fields
  const payload = { ...formData.value }
  
  const optionalFields = [
    'location', 'city', 'province', 'postal_code', 
    'operating_hours', 'manager_name', 'manager_phone', 'manager_email'
  ]
  
  optionalFields.forEach(field => {
    if (payload[field] === '') {
      payload[field] = null
    }
  })

  emit('submit', payload)
}
</script>
