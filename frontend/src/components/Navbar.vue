<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();
const { user, isAuthenticated } = storeToRefs(authStore);

// Hilfsvariable für den vollen Namen
const fullName = computed(() => {
  if (user.value?.first_name && user.value?.last_name) {
    return `${user.value.first_name} ${user.value.last_name}`;
  }
  return user.value?.name || 'User';
});

// Dropdown Management
const isDropdownOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);

const toggleDropdown = () => (isDropdownOpen.value = !isDropdownOpen.value);
const closeDropdown = () => (isDropdownOpen.value = false);

const handleLogout = async () => {
  await authStore.logout();
  closeDropdown();
  router.push('/login');
};

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    closeDropdown();
  }
};

onMounted(() => window.addEventListener('click', handleClickOutside));
onUnmounted(() => window.removeEventListener('click', handleClickOutside));

interface NavLink {
  name: string;
  href: string;
}

const navLinks = ref<NavLink[]>([
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Shows', href: '/shows' },
  { name: 'Fixture Types', href: '/fixtures' },
  { name: 'H-Nodes', href: '/h-nodes' },
]);
</script>

<template>
  <nav class="bg-[#0b0e14]/80 px-6 py-4 flex items-center justify-between border-b border-white/10 backdrop-blur-md sticky top-0 z-50">
    <router-link to="/" class="text-2xl tracking-tighter font-bold text-blue-100 hover:scale-105 transition-transform">HYPERION<span class="text-blue-600 text-2xl font-bold">.</span>
    </router-link>

    <ul v-if="isAuthenticated" class="hidden md:flex items-center space-x-10">
      <li v-for="link in navLinks" :key="link.name">
        <router-link 
          :to="link.href" 
          class="relative group text-gray-400 hover:text-white text-sm font-medium transition-colors py-2"
          active-class="text-white"
        >
          {{ link.name }}
          <span class="absolute -bottom-1 left-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300 w-0 group-hover:w-full"></span>
          <span v-if="router.currentRoute.value.path === link.href" class="absolute -bottom-1 left-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 w-full"></span>
        </router-link>
      </li>
    </ul>

    <div class="flex items-center space-x-6">
      <template v-if="!isAuthenticated">
        <router-link to="/login" class="text-sm font-semibold text-gray-300 hover:text-white transition-colors">
          Login
        </router-link>
        
        <router-link to="/register" class="relative inline-flex items-center justify-center p-0.5 overflow-hidden text-sm font-medium text-white rounded-full group bg-gradient-to-br from-blue-600 to-purple-600 hover:shadow-[0_0_15px_rgba(37,99,235,0.4)] transition-all">
          <span class="relative px-5 py-2 transition-all ease-in duration-75 bg-[#0b0e14] rounded-full group-hover:bg-transparent">
            Register
          </span>
        </router-link>
      </template>

      <div v-else ref="dropdownRef" class="relative">
        <button 
          @click.stop="toggleDropdown" 
          class="flex items-center space-x-3 group focus:outline-none focus:ring-2 focus:ring-blue-500/20 rounded-full p-1 transition-all"
        >
          <div class="text-right hidden sm:block">
            <div class="text-sm font-bold text-white group-hover:text-blue-400 transition-colors leading-tight">
              {{ user?.username || user?.name || 'User' }}
            </div>
            <div class="text-[10px] text-gray-500 uppercase tracking-widest">
              {{ user?.role || 'Operator' }}
            </div>
          </div>
          
          <div class="w-10 h-10 rounded-full border-2 border-white/10 group-hover:border-blue-500/50 transition-all flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900 text-blue-400 font-bold shadow-lg">
            {{ (user?.username || user?.name || 'U').charAt(0).toUpperCase() }}
          </div>
        </button>

        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="transform scale-95 opacity-0 -translate-y-2"
          enter-to-class="transform scale-100 opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="transform scale-100 opacity-100"
          leave-to-class="transform scale-95 opacity-0"
        >
          <div v-if="isDropdownOpen" class="absolute right-0 mt-3 w-64 bg-[#11141b] border border-white/10 rounded-2xl shadow-2xl py-2 z-[60] overflow-hidden">
            <div class="px-5 py-3 border-b border-white/5 bg-white/[0.02] mb-1">
               <p class="text-white text-sm font-bold truncate">{{ fullName }}</p>
               <p class="text-gray-500 text-xs truncate">@{{ user?.username || 'user' }}</p>
               <div class="mt-2 inline-flex items-center px-2 py-0.5 rounded text-[9px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-widest">
                 {{ user?.role || 'Operator' }}
               </div>
            </div>
            
            <router-link @click="closeDropdown" to="/profile" class="flex items-center px-5 py-2.5 text-sm text-gray-300 hover:bg-blue-600/10 hover:text-blue-400 transition-colors">
               Userprofile
            </router-link>
            
            <router-link @click="closeDropdown" to="/settings" class="flex items-center px-5 py-2.5 text-sm text-gray-300 hover:bg-blue-600/10 hover:text-blue-400 transition-colors">
               Settings
            </router-link>
            
            <div class="h-px bg-white/5 my-1 mx-2"></div>
            
            <button 
              @click="handleLogout" 
              class="w-full text-left px-5 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors font-medium"
            >
              Logout
            </button>
          </div>
        </transition>
      </div>
    </div>
  </nav>
</template>