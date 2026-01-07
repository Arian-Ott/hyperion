<script setup lang="ts">
import { watch } from 'vue';
import { useAuthStore } from './stores/auth';
import { storeToRefs } from 'pinia';
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";

const authStore = useAuthStore();
const { isAuthenticated, accessToken } = storeToRefs(authStore);

// WICHTIG: KEIN onMounted mit checkAuthStatus() mehr!
// Das macht jetzt der Router Guard, bevor die App überhaupt mounted.

// Der WebSocket-Wächter bleibt aber hier:
watch([isAuthenticated, accessToken], ([isLogged, token]) => {
  if (isLogged && token) {
    authStore.connectEngine();
  }
}, { immediate: true });
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[#0b0e14] text-white">
    <Navbar />
    <RouterView />
    <Footer />
  </div>
</template>