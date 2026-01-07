<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();


const form = ref({
  username: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: ''
});

const errorMessage = ref('');
const isLoading = ref(false);

// Passwort-Policy Regex
const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,64}$/;

const isPasswordValid = computed(() => passwordPattern.test(form.value.password));
const passwordsMatch = computed(() => form.value.password.length > 0 && form.value.password === form.value.password_confirm);

const handleRegister = async () => {
    const BASE_URL = import.meta.env.VITE_URL;
  if (!isPasswordValid.value || !passwordsMatch.value) return;
  
  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await fetch(`${BASE_URL}/api/accounts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    });

    if (response.ok) {
      router.push('/login');
    } else {
      const data = await response.json();
      errorMessage.value = data.detail || "Registrierung fehlgeschlagen.";
    }
  } catch (err) {
    errorMessage.value = "Verbindung zum Server fehlgeschlagen.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="min-h-[calc(100vh-80px)] flex items-center justify-center px-6 bg-[#0b0e14]">
    <div class="absolute inset-0 overflow-hidden -z-10">
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-600/5 rounded-full blur-[120px]"></div>
    </div>

    <div class="w-full max-w-2xl bg-[#0f121a] border border-white/10 rounded-3xl p-10 shadow-2xl">
      <div class="text-center mb-10">
        <h1 class="text-4xl font-bold text-white tracking-tighter">Account erstellen<span class="text-blue-600">.</span></h1>
        <p class="text-gray-400 mt-2">Werde Teil des Hyperion-Netzwerks.</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-2">
            <label class="text-[11px] font-bold text-gray-500 uppercase tracking-[0.2em] ml-1">Vorname</label>
            <input v-model="form.first_name" type="text" placeholder="John" 
              class="w-full bg-[#0b0e14] border border-white/10 rounded-2xl px-5 py-4 text-white placeholder:text-gray-700 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all" />
          </div>
          <div class="space-y-2">
            <label class="text-[11px] font-bold text-gray-500 uppercase tracking-[0.2em] ml-1">Nachname</label>
            <input v-model="form.last_name" type="text" placeholder="Doe" 
              class="w-full bg-[#0b0e14] border border-white/10 rounded-2xl px-5 py-4 text-white placeholder:text-gray-700 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all" />
          </div>
          <div class="space-y-2 md:col-span-2">
            <label class="text-[11px] font-bold text-gray-500 uppercase tracking-[0.2em] ml-1">Username</label>
            <input v-model="form.username" type="text" placeholder="johndoe123" 
              class="w-full bg-[#0b0e14] border border-white/10 rounded-2xl px-5 py-4 text-white placeholder:text-gray-700 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all" />
          </div>
          <div class="space-y-2">
            <label class="text-[11px] font-bold text-gray-500 uppercase tracking-[0.2em] ml-1">Passwort</label>
            <input v-model="form.password" type="password" placeholder="••••••••" 
              class="w-full bg-[#0b0e14] border border-white/10 rounded-2xl px-5 py-4 text-white placeholder:text-gray-700 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all" />
          </div>
          <div class="space-y-2">
            <label class="text-[11px] font-bold text-gray-500 uppercase tracking-[0.2em] ml-1">Bestätigen</label>
            <input v-model="form.password_confirm" type="password" placeholder="••••••••" 
              class="w-full bg-[#0b0e14] border border-white/10 rounded-2xl px-5 py-4 text-white placeholder:text-gray-700 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all" />
          </div>
        </div>

        <div class="flex flex-col sm:flex-row justify-between items-start gap-4 px-1">
          <div class="text-[10px] space-y-1">
            <p :class="form.password.length >= 8 ? 'text-green-500' : 'text-gray-600'">• 8-64 Zeichen</p>
            <p :class="isPasswordValid ? 'text-green-500' : 'text-gray-600'">• Mix aus A, a, 1, !</p>
          </div>
          <p v-if="errorMessage" class="text-red-500 text-xs font-medium">{{ errorMessage }}</p>
          <p v-else-if="form.password_confirm && !passwordsMatch" class="text-red-400 text-[10px]">Passwörter nicht identisch</p>
        </div>

        <button 
          type="submit"
          :disabled="isLoading || !isPasswordValid || !passwordsMatch"
          class="w-full relative inline-flex items-center justify-center p-0.5 overflow-hidden text-sm font-bold text-white rounded-2xl group bg-gradient-to-br from-blue-600 to-purple-600 hover:shadow-[0_0_25px_rgba(37,99,235,0.4)] transition-all disabled:opacity-20 disabled:cursor-not-allowed"
        >
          <span class="relative w-full px-5 py-4 transition-all ease-in duration-75 bg-[#0f121a] rounded-2xl group-hover:bg-transparent">
            {{ isLoading ? 'Verarbeite...' : 'Registrieren' }}
          </span>
        </button>
      </form>

      <div class="mt-8 text-center text-sm text-gray-500">
        Bereits einen Account? 
        <router-link to="/login" class="text-blue-500 hover:text-blue-400 font-bold ml-1 transition-colors">Zum Login</router-link>
      </div>
    </div>
  </div>
</template>