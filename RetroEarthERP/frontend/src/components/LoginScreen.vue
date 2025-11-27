<template>
  <div class="h-screen w-screen bg-[#c4b5a0] flex items-center justify-center font-sans select-none">
    <div class="bg-stone-300 border-4 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 shadow-2xl w-[400px] p-1">
      <!-- Title Bar -->
      <div class="bg-gradient-to-r from-olive-700 to-olive-600 text-stone-100 px-2 py-1 flex justify-between items-center mb-4 border-b-2 border-stone-500">
        <span class="font-bold text-sm">RetroEarthERP</span>
        <div class="flex gap-2">
          <button @click="toggleLanguage" class="text-xs font-bold hover:text-yellow-300">
            {{ locale === 'en' ? '🇹🇭 TH' : '🇺🇸 EN' }}
          </button>
          <button class="w-5 h-5 bg-stone-300 hover:bg-stone-200 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 flex items-center justify-center text-stone-800 font-bold text-xs">×</button>
        </div>
      </div>

      <!-- Content -->
      <div class="px-6 py-4">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-16 h-16 bg-stone-200 border-2 border-stone-500 flex items-center justify-center">
            <Key class="w-10 h-10 text-olive-700" />
          </div>
          <div class="text-stone-800">
            <p class="font-bold text-lg">{{ $t('auth.welcomeBack') }}</p>
            <p class="text-xs text-stone-600">{{ $t('auth.loginPrompt') }}</p>
          </div>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="space-y-1">
            <label class="block text-xs font-bold text-stone-700">{{ $t('common.username') }}:</label>
            <input 
              v-model="username"
              type="text" 
              class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50"
              autofocus
            />
          </div>
          
          <div class="space-y-1">
            <label class="block text-xs font-bold text-stone-700">{{ $t('common.password') }}:</label>
            <input 
              v-model="password"
              type="password" 
              class="w-full bg-white border-2 border-stone-500 border-b-stone-100 border-r-stone-100 px-2 py-1 text-sm outline-none focus:bg-yellow-50"
            />
          </div>

          <div v-if="error" class="text-red-600 text-xs font-bold text-center bg-red-100 border border-red-400 p-1">
            {{ error }}
          </div>

          <div class="flex justify-end gap-2 mt-6 pt-4 border-t border-stone-400">
            <button 
              type="submit"
              :disabled="isLoading"
              class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400"
            >
              {{ isLoading ? $t('common.loading') : 'OK' }}
            </button>
            <button 
              type="button"
              class="px-6 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400"
            >
              {{ $t('common.cancel') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Key } from 'lucide-vue-next'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const emit = defineEmits(['login-success'])
const { t, locale } = useI18n()

const username = ref('admin')
const password = ref('admin123')
const error = ref('')
const isLoading = ref(false)

function toggleLanguage() {
  locale.value = locale.value === 'en' ? 'th' : 'en'
}

async function handleLogin() {
  error.value = ''
  isLoading.value = true
  
  try {
    // Correct Endpoint: /api/auth/login
    const response = await axios.post('http://localhost:8000/api/auth/login', {
      username: username.value,
      password: password.value
    })
    
    if (response.data.access_token) {
      console.log('Login successful, token received:', response.data.access_token)
      localStorage.setItem('token', response.data.access_token)
      console.log('Emitting login-success event')
      emit('login-success', response.data)
    }
  } catch (err) {
    console.error(err)
    if (err.response) {
      error.value = t('auth.invalidCredentials')
    } else if (err.message) {
      error.value = err.message
    } else {
      error.value = t('common.error')
    }
  } finally {
    isLoading.value = false
  }
}
</script>
