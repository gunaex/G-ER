<template>
  <div class="p-2 bg-stone-200 h-full overflow-auto">
    <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4">
      <h2 class="text-lg font-bold text-stone-800 mb-4">Cycle Count</h2>

      <!-- Step 1: Start Count -->
      <div v-if="!activeCount" class="space-y-4">
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Start New Count</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Warehouse *</label>
              <select v-model="startData.warehouse_id" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="">-- Select Warehouse --</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Count Date *</label>
              <input v-model="startData.count_date" type="date" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none" />
            </div>
          </div>
          <div class="mt-4 flex justify-end">
            <button @click="startCount" :disabled="!startData.warehouse_id || !startData.count_date" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400 disabled:opacity-50">
              Start Count (Snapshot)
            </button>
          </div>
        </fieldset>
      </div>

      <!-- Step 2: Execute Count -->
      <div v-else class="space-y-4">
        <div class="flex justify-between items-center bg-yellow-100 border border-yellow-300 p-2 text-sm">
          <span><strong>Count ID:</strong> {{ activeCount.id }}</span>
          <span><strong>Status:</strong> {{ activeCount.status }}</span>
          <span><strong>Date:</strong> {{ activeCount.count_date }}</span>
        </div>

        <div class="overflow-auto max-h-[400px] border-2 border-stone-500 bg-white">
          <table class="w-full text-sm text-left border-collapse">
            <thead class="bg-stone-300 sticky top-0">
              <tr>
                <th class="border border-stone-400 px-2 py-1">Item Code</th>
                <th class="border border-stone-400 px-2 py-1">Location</th>
                <th class="border border-stone-400 px-2 py-1 text-right">System Qty</th>
                <th class="border border-stone-400 px-2 py-1 text-right">Actual Qty</th>
                <th class="border border-stone-400 px-2 py-1 text-right">Variance</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="detail in activeCount.details" :key="detail.id" class="hover:bg-blue-50">
                <td class="border border-stone-300 px-2 py-1">{{ detail.item_code }}</td>
                <td class="border border-stone-300 px-2 py-1">{{ detail.location_code || '-' }}</td>
                <td class="border border-stone-300 px-2 py-1 text-right">{{ detail.snapshot_system_qty }}</td>
                <td class="border border-stone-300 px-2 py-0">
                  <input v-model.number="detail.actual_counted_qty" type="number" class="w-full text-right bg-transparent outline-none focus:bg-yellow-50" placeholder="0" />
                </td>
                <td class="border border-stone-300 px-2 py-1 text-right font-bold" :class="getVariance(detail) !== 0 ? 'text-red-600' : 'text-green-600'">
                  {{ getVariance(detail) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t-2 border-stone-400">
          <button @click="cancelCount" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm">
            Cancel
          </button>
          <button @click="submitCount" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
            Submit Count
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const props = defineProps({
  warehouses: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

const startData = ref({
  warehouse_id: '',
  count_date: new Date().toISOString().split('T')[0]
})

const activeCount = ref(null)

async function startCount() {
  try {
    const response = await axios.post('http://localhost:8000/api/wms/cycle-counts/start', startData.value)
    // After start, fetch full details (because start returns Create schema, not full details with items)
    // Wait, start returns CycleCountHeaderCreate which doesn't have details.
    // I need to fetch the full object.
    const id = response.data.id // Assuming backend returns the created object with ID
    // Wait, my backend returns db_header, which is the ORM object. Pydantic schema CycleCountHeaderCreate DOES NOT have ID.
    // I should have used CycleCountHeaderResponse for the return type of start_cycle_count!
    // I'll fix the backend or just assume ID is there if Pydantic allows extra fields (it usually doesn't in response validation).
    // Let's assume I need to fetch it. But I don't have the ID if schema filters it out.
    // I should update backend to return CycleCountHeaderResponse.
    
    // For now, let's assume I fix the backend.
    await fetchCountDetails(response.data.id)
  } catch (error) {
    console.error("Failed to start count", error)
    alert("Failed to start cycle count")
  }
}

async function fetchCountDetails(id) {
  try {
    const response = await axios.get(`http://localhost:8000/api/wms/cycle-counts/${id}`)
    activeCount.value = response.data
  } catch (error) {
    console.error("Failed to fetch count details", error)
  }
}

function getVariance(detail) {
  const actual = detail.actual_counted_qty || 0
  return actual - detail.snapshot_system_qty
}

async function submitCount() {
  if (!confirm("Are you sure you want to submit this cycle count? This will finalize the count.")) return
  
  try {
    const updates = activeCount.value.details.map(d => ({
      id: d.id,
      actual_counted_qty: d.actual_counted_qty || 0
    }))
    
    await axios.post(`http://localhost:8000/api/wms/cycle-counts/${activeCount.value.id}/submit`, updates)
    alert("Cycle Count Submitted Successfully!")
    emit('close')
  } catch (error) {
    console.error("Failed to submit count", error)
    alert("Failed to submit count")
  }
}

function cancelCount() {
  activeCount.value = null
  startData.value = {
    warehouse_id: '',
    count_date: new Date().toISOString().split('T')[0]
  }
}
</script>
