<script setup lang="ts">
import { useAuthStore } from '../stores/auth';
import { storeToRefs } from 'pinia';

const authStore = useAuthStore();
// Wir holen den reaktiven User-Zustand aus dem Store
const { user } = storeToRefs(authStore);

// Beispiel-Statistiken für die Optik
const stats = [
  { name: 'Aktive Shows', value: '12', icon: '🎭' },
  { name: 'H-Nodes Online', value: '5/6', icon: '🌐' },
  { name: 'DMX Universen', value: '24', icon: '🔌' },
];
</script>

<template>
  <div class="min-h-screen p-8">
    <header class="mb-12">
      <h1 class="text-4xl font-bold text-white tracking-tighter">
        Hallo, <span class="text-blue-500">{{ user?.first_name || user?.name || 'Operator' }}</span>!
      </h1>
      <p class="text-gray-400 mt-2 text-lg">
        Willkommen im Hyperion Kontrollzentrum. Alles läuft nach Plan.
      </p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      <div 
        v-for="stat in stats" 
        :key="stat.name"
        class="bg-[#0f121a] border border-white/5 p-6 rounded-2xl hover:border-blue-500/30 transition-all group"
      >
        <div class="text-2xl mb-4 group-hover:scale-110 transition-transform inline-block">
          {{ stat.icon }}
        </div>
        <div class="text-3xl font-bold text-white mb-1">{{ stat.value }}</div>
        <div class="text-xs font-bold text-gray-500 uppercase tracking-widest">
          {{ stat.name }}
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <section class="bg-[#0f121a] border border-white/5 rounded-3xl p-8 min-h-[300px]">
        <h2 class="text-xl font-bold text-white mb-6 flex items-center">
          <span class="w-2 h-2 bg-blue-500 rounded-full mr-3 animate-pulse"></span>
          Aktive Engine
        </h2>
        <div class="flex flex-col items-center justify-center h-full text-center space-y-4">
          <div class="text-gray-600 italic">Keine laufenden Prozesse erkannt.</div>
          <button class="bg-blue-600/10 text-blue-400 px-6 py-2 rounded-full text-sm font-bold hover:bg-blue-600 hover:text-white transition-all">
            Engine starten
          </button>
        </div>
      </section>

      <section class="bg-[#0f121a] border border-white/5 rounded-3xl p-8 min-h-[300px]">
        <h2 class="text-xl font-bold text-white mb-6">Letzte Aktivitäten</h2>
        <div class="space-y-4">
          <div v-for="i in 3" :key="i" class="flex items-center justify-between border-b border-white/5 pb-4 last:border-0">
            <div>
              <p class="text-sm text-white font-medium">Show "Mainstage_V2" gespeichert</p>
              <p class="text-[10px] text-gray-500">Vor {{ i * 15 }} Minuten</p>
            </div>
            <div class="text-blue-500 text-xs font-bold cursor-pointer">Details</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>