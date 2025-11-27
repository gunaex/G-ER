<template>
  <div class="p-2 bg-stone-200 h-full overflow-auto">
    <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4">
      <h2 class="text-lg font-bold text-stone-800 mb-4">
        {{ mode === 'add' ? 'Add Location' : 'Edit Location' }}
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Location Details</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Warehouse *</label>
              <select v-model="formData.warehouse_id" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="">-- Select Warehouse --</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Location Code *</label>
              <input v-model="formData.location_code" type="text" required maxlength="50" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50" />
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Zone Type *</label>
              <select v-model="formData.zone_type" required class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="RECEIVE">Receiving Zone</option>
                <option value="STORE">Storage Zone</option>
                <option value="PICK">Picking Zone</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Floor Level</label>
              <input v-model.number="formData.floor_level" type="number" min="1" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm text-right outline-none focus:bg-yellow-50" />
            </div>
          </div>
        </fieldset>

        <fieldset class="border-2 border-stone-500 p-3 bg-stone-200">
          <legend class="text-sm font-bold text-stone-700 px-2">Storage Conditions & Security</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-stone-700 mb-1">Condition Type</label>
              <select v-model="formData.condition_type" class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none">
                <option value="GENERAL">General</option>
                <option value="COLD">Cold Storage</option>
                <option value="HAZMAT">Hazardous Material</option>
                <option value="SECURE">Secure Storage</option>
              </select>
            </div>
            <div class="flex items-center pt-6">
              <input v-model="formData.is_secure_cage" type="checkbox" id="is_secure" class="mr-2" />
              <label for="is_secure" class="text-sm font-bold text-stone-700">Is Secure Cage?</label>
            </div>
          </div>
        </fieldset>

        <div class="flex justify-end gap-2 pt-4 border-t-2 border-stone-400">
          <button type="button" @click="$emit('cancel')" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
            Cancel
          </button>
          <button type="submit" class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
            Save Location
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
    default: 'add'
  },
  warehouses: {
    type: Array,
    default: () => []
  },
  initialData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formData = ref({
  warehouse_id: '',
  location_code: '',
  zone_type: 'STORE',
  condition_type: 'GENERAL',
  is_secure_cage: false,
  floor_level: 1
})

function handleSubmit() {
  emit('submit', formData.value)
}

onMounted(() => {
  if (props.mode === 'edit' && props.initialData) {
    formData.value = { ...props.initialData }
  }
})
</script>
