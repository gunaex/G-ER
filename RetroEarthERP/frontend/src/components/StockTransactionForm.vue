<template>
  <div class="p-2 bg-stone-200 h-full overflow-auto">
    <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4">
      <h2 class="text-lg font-bold text-stone-800 mb-4">
        {{ mode === 'issue' ? 'Stock Issue (Out)' : 'Stock Receipt (In)' }}
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Header Information -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Transaction Header</legend>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Date *</label>
              <input v-model="formData.transaction_date" type="date" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Reference No. *</label>
              <input v-model="formData.reference_no" type="text" required maxlength="50" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Partner (Optional)</label>
              <select v-model="formData.partner_code" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="">-- Select Partner --</option>
                <option v-for="p in partners" :key="p.code" :value="p.code">{{ p.name }}</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Items List -->
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Items</legend>
          
          <div class="overflow-x-auto border-2 border-stone-400 bg-white mb-2">
            <table class="w-full text-xs border-collapse">
              <thead>
                <tr class="bg-stone-300 border-b-2 border-stone-500">
                  <th class="border-r border-stone-400 px-2 py-1 text-left w-10">#</th>
                  <th class="border-r border-stone-400 px-2 py-1 text-left">Item Code</th>
                  <th class="border-r border-stone-400 px-2 py-1 text-left">Warehouse</th>
                  <th class="border-r border-stone-400 px-2 py-1 text-right w-24">Quantity</th>
                  <th class="border-r border-stone-400 px-2 py-1 text-left w-16">Unit</th>
                  <th class="px-2 py-1 w-10"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(line, idx) in formData.items" :key="idx" class="border-b border-stone-200">
                  <td class="border-r border-stone-300 px-2 py-1 text-center">{{ idx + 1 }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">
                    <select v-model="line.item_code" required class="w-full bg-transparent outline-none" @change="updateUnit(line)">
                      <option value="">-- Select Item --</option>
                      <option v-for="i in items" :key="i.id" :value="i.id">{{ i.id }} - {{ i.desc }}</option>
                    </select>
                  </td>
                  <td class="border-r border-stone-300 px-2 py-1">
                    <select v-model="line.warehouse_code" required class="w-full bg-transparent outline-none">
                      <option value="">-- Select Warehouse --</option>
                      <option v-for="w in warehouses" :key="w.code" :value="w.code">{{ w.name }}</option>
                    </select>
                  </td>
                  <td class="border-r border-stone-300 px-2 py-1">
                    <input v-model.number="line.qty" type="number" step="0.01" required class="w-full text-right bg-transparent outline-none" />
                  </td>
                  <td class="border-r border-stone-300 px-2 py-1 text-center bg-stone-100">
                    {{ line.unit || '-' }}
                  </td>
                  <td class="px-2 py-1 text-center">
                    <button type="button" @click="removeLine(idx)" class="text-red-600 font-bold hover:text-red-800">×</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <button type="button" @click="addLine" class="px-3 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-xs active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
            + Add Line
          </button>
        </fieldset>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-4 border-t-2 border-stone-400">
          <button type="button" @click="$emit('cancel')" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
            Cancel
          </button>
          <button type="submit" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
            Save Transaction
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    required: true, // 'issue' or 'receipt'
    validator: (value) => ['issue', 'receipt'].includes(value)
  },
  items: {
    type: Array,
    default: () => []
  },
  partners: {
    type: Array,
    default: () => []
  },
  warehouses: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formData = ref({
  transaction_date: new Date().toISOString().split('T')[0],
  reference_no: '',
  partner_code: '',
  items: []
})

function addLine() {
  formData.value.items.push({
    item_code: '',
    warehouse_code: '',
    qty: 0,
    unit: ''
  })
}

function removeLine(index) {
  formData.value.items.splice(index, 1)
}

function updateUnit(line) {
  const item = props.items.find(i => i.id === line.item_code)
  if (item) {
    // Access _raw for unit if available, otherwise try direct property
    line.unit = item._raw?.unit_of_measure || item.unit || 'PCS'
    // Default warehouse if only one exists? No, force selection.
  }
}

function handleSubmit() {
  // Basic validation
  if (formData.value.items.length === 0) {
    alert('Please add at least one item.')
    return
  }
  
  for (const line of formData.value.items) {
    if (!line.item_code || !line.warehouse_code || line.qty <= 0) {
      alert('Please fill in all item details (Item, Warehouse, positive Qty).')
      return
    }
  }

  emit('submit', { ...formData.value, type: props.mode })
}

onMounted(() => {
  addLine() // Start with one empty line
})
</script>
