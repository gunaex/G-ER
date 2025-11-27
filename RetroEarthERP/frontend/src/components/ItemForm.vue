<template>
  <div class="p-2 bg-stone-200 h-full overflow-auto">
    <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4">
      <h2 class="text-lg font-bold text-stone-800 mb-4">
        {{ mode === 'add' ? 'Add New Item' : 'Edit Item' }}
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Basic Information -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Basic Information</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Item Code *</label>
              <input v-model="formData.item_code" :disabled="mode === 'edit'" type="text" required maxlength="20" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Item Type *</label>
              <select v-model="formData.item_type" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="RAW_MATERIAL">Raw Material</option>
                <option value="COMPONENT">Component</option>
                <option value="FINISHED_GOOD">Finished Good</option>
                <option value="WIP">WIP (Work In Progress)</option>
                <option value="PACKAGE">Package</option>
                <option value="SERVICE">Service</option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">Item Name *</label>
              <input v-model="formData.item_name" type="text" required maxlength="200" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Category</label>
              <input v-model="formData.category" type="text" maxlength="100" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Unit of Measure *</label>
              <select v-model="formData.unit_of_measure" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="PCS">PCS (Pieces)</option>
                <option value="KG">KG (Kilograms)</option>
                <option value="L">L (Liters)</option>
                <option value="M">M (Meters)</option>
                <option value="BOX">BOX</option>
                <option value="SET">SET</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Pricing (Sensitive) -->
        <fieldset class="border-2 border-red-600 p-3 bg-red-50">
          <legend class="text-sm font-bold text-red-700 px-2">💰 Pricing (Sensitive Data)</legend>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Standard Cost (THB) *</label>
              <input v-model.number="formData.standard_cost" type="number" step="0.01" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Selling Price (THB) *</label>
              <input v-model.number="formData.selling_price" type="number" step="0.01" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Minimum Price (THB)</label>
              <input v-model.number="formData.minimum_price" type="number" step="0.01" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Inventory Control -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Inventory Control</legend>
          <div class="grid grid-cols-4 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Reorder Point</label>
              <input v-model.number="formData.reorder_point" type="number" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Reorder Qty</label>
              <input v-model.number="formData.reorder_quantity" type="number" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Safety Stock</label>
              <input v-model.number="formData.safety_stock" type="number" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Lead Time (days)</label>
              <input v-model.number="formData.lead_time_days" type="number" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Specifications -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Specifications</legend>
          <div class="grid grid-cols-4 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Weight (kg)</label>
              <input v-model.number="formData.weight_kg" type="number" step="0.001" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Length (cm)</label>
              <input v-model.number="formData.length_cm" type="number" step="0.1" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Width (cm)</label>
              <input v-model.number="formData.width_cm" type="number" step="0.1" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Height (cm)</label>
              <input v-model.number="formData.height_cm" type="number" step="0.1" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">Barcode/SKU</label>
              <input v-model="formData.barcode" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-bold text-stone-700 mb-1">HS Code</label>
              <input v-model="formData.hs_code" type="text" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <!-- Status -->
        <div class="flex items-center gap-2">
          <input v-model="formData.is_active" type="checkbox" id="item-active" class="w-4 h-4" />
          <label for="item-active" class="text-sm font-bold text-stone-700">Active</label>
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
  item: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formData = ref({
  item_code: '',
  item_name: '',
  item_type: 'RAW_MATERIAL',
  category: '',
  unit_of_measure: 'PCS',
  standard_cost: 0,
  selling_price: 0,
  minimum_price: null,
  reorder_point: 0,
  reorder_quantity: 0,
  safety_stock: 0,
  lead_time_days: 0,
  weight_kg: null,
  length_cm: null,
  width_cm: null,
  height_cm: null,
  barcode: '',
  hs_code: '',
  is_active: true
})

// Load existing data in edit mode
watch(() => props.item, (newItem) => {
  if (newItem && props.mode === 'edit') {
    formData.value = { ...newItem._raw }
  }
}, { immediate: true })

function handleSubmit() {
  // Sanitize data: convert empty strings to null for optional fields
  const payload = { ...formData.value }
  
  const optionalFields = [
    'category', 'barcode', 'hs_code', 
    'weight_kg', 'length_cm', 'width_cm', 'height_cm', 'minimum_price'
  ]
  
  optionalFields.forEach(field => {
    if (payload[field] === '') {
      payload[field] = null
    }
  })

  emit('submit', payload)
}
</script>
