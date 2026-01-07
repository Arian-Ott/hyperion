<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  if (!username.value || !password.value) {
    errorMessage.value = "Bitte fülle alle Felder aus.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  const success = await authStore.login(username.value, password.value);

  if (success) {
    router.push('/dashboard');
  } else {
    errorMessage.value = "Login fehlgeschlagen. Überprüfe deine Daten.";
  }
  isLoading.value = false;
};
</script>

<template>
  <div class="min-h-[calc(100vh-80px)] flex items-center justify-center px-6">
    <div class="absolute inset-0 overflow-hidden -z-10">
      <div class="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px]"></div>
    </div>

    <div class="w-full max-w-md bg-[#0f121a] border border-white/10 rounded-2xl p-8 shadow-2xl">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-white tracking-tighter">
          Willkommen zurück<span class="text-blue-600">.</span>
        </h1>
        <p class="text-gray-400 mt-2 text-sm">Melde dich an, um dein System zu verwalten.</p>
      </div>

      <div v-if="errorMessage" class="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Username</label>
          <input 
            v-model="username"
            type="text" 
            placeholder="z.B. admin"
            class="w-full bg-[#0b0e14] border border-white/5 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Passwort</label>
          <input 
            v-model="password"
            type="password" 
            placeholder="••••••••"
            class="w-full bg-[#0b0e14] border border-white/5 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all"
          />
        </div>

        <button 
          type="submit"
          :disabled="isLoading"
          class="w-full relative inline-flex items-center justify-center p-0.5 overflow-hidden text-sm font-medium text-white rounded-xl group bg-gradient-to-br from-blue-600 to-purple-600 hover:shadow-[0_0_20px_rgba(37,99,235,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span class="relative w-full px-5 py-3 transition-all ease-in duration-75 bg-[#0f121a] rounded-xl group-hover:bg-transparent">
            <span v-if="isLoading">Lädt...</span>
            <span v-else>Anmelden</span>
          </span>
        </button>
      </form>

      <div class="mt-8 text-center text-sm">
        <span class="text-gray-500">Noch keinen Zugang?</span>
        <a href="/register" class="ml-2 text-blue-400 hover:text-blue-300 font-medium transition-colors">Jetzt registrieren</a>
      </div>
    </div>
  </div>
</template>