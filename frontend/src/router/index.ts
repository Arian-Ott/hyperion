import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

// src/router/index.ts
const routes = [
  { path: '/login', component: () => import("../views/LoginView.vue"), meta: { guestOnly: true } },
  { path: '/register', component: () => import('../views/RegisterView.vue'), meta: { guestOnly: true } },
  { path: '/dashboard', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  
  // Diese Pfade haben in deiner Navbar gefehlt:
  { path: '/shows', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/fixtures', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/h-nodes', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  
  { path: '/', redirect: '/dashboard' }
];
const router = createRouter({
  history: createWebHistory(),
  routes
});

// Der Guard: Schützt die Routen
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // WICHTIG: Warte auf den Cookie-Check beim ersten Seitenladen
  if (authStore.isInitialLoading) {
    await authStore.checkAuthStatus();
  }

  const isLoggedIn = authStore.isAuthenticated;

  // Regel 1: Wenn Seite nur für Gäste ist (Login/Register) und User eingeloggt ist
  if (to.meta.guestOnly && isLoggedIn) {
    next('/dashboard');
  } 
  // Regel 2: Wenn Seite Auth erfordert und User NICHT eingeloggt ist
  else if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login');
  } 
  // Sonst: Einfach durchlassen
  else {
    next();
  }
});
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // 1. Initialer Check: Nur wenn wir den Status noch gar nicht kennen
  if (authStore.isInitialLoading) {
    await authStore.checkAuthStatus();
  }

  // 2. Routing Logik
  const isLoggedIn = authStore.isAuthenticated;

  if (to.meta.guestOnly && isLoggedIn) {
    next('/dashboard');
  } else if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login');
  } else {
    next();
  }
});
export default router;