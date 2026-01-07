import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  // 1. HARDCODED URL - Damit schließen wir Vite-Proxy-Fehler aus
  const BACKEND_HOST = 'localhost:2468'; 
  const BASE_URL = `http://${BACKEND_HOST}`;
  const WS_URL = `ws://${BACKEND_HOST}`;

  const user = ref<{ id: string; username: string; role: string } | null>(null);
  const accessToken = ref<string | null>(null);
  const isInitialLoading = ref(true);
  const socket = ref<WebSocket | null>(null);
  
  // Deduping & Timer Variablen
  let refreshPromise: Promise<boolean> | null = null;
  let refreshTimer: ReturnType<typeof setInterval> | null = null;
  let reconnectAttempts = 0;

  const isAuthenticated = computed(() => !!user.value);

  // --- WEBSOCKET ENGINE ---
  const connectEngine = () => {
    // Wenn Socket schon offen oder verbindet (0=CONNECTING, 1=OPEN), brich ab
    if (socket.value && (socket.value.readyState === 0 || socket.value.readyState === 1)) return;

    if (!isAuthenticated.value || !accessToken.value) {
      console.warn("⛔ WS Start verhindert: Kein Token/Login.");
      return;
    }

    const url = `${WS_URL}/ws/engine?token=${accessToken.value}`;
    console.log(`🚀 Starte WebSocket Verbindung...`);

    socket.value = new WebSocket(url);

    socket.value.onopen = () => {
      console.log("✅ ENGINE VERBUNDEN");
      reconnectAttempts = 0; // Reset Counter bei Erfolg
    };
    
    socket.value.onmessage = (e) => {
      // console.log("DMX Data:", e.data);
    };

    socket.value.onclose = async (e) => {
      socket.value = null;
      console.log(`🔌 Getrennt (Code: ${e.code}).`);
      
      // Falls wir noch eingeloggt sind, versuchen wir einen Reconnect
      if (isAuthenticated.value) {
        // Bei Auth-Fehler (z.B. Backend killt Verbindung wegen Token): Sofort neuen Token holen
        if (e.code === 4001 || e.code === 1006) {
           console.log("⚠️ Auth-Problem vermutet. Erzwinge Token-Refresh vor Reconnect...");
           await refreshToken();
        }

        // Exponentieller Backoff: Erst schnell (1s), dann langsamer (bis max 5s)
        const delay = Math.min(1000 * (2 ** reconnectAttempts), 5000);
        console.log(`🔄 Reconnect in ${delay}ms...`);
        reconnectAttempts++;
        setTimeout(connectEngine, delay);
      }
    };

    socket.value.onerror = () => console.error("❌ WS Fehler");
  };

  // --- TOKEN REFRESH (Mit Promise Deduping) ---
  const refreshToken = async (): Promise<boolean> => {
    // Wenn schon ein Refresh läuft, hängen wir uns an diesen dran (spart Requests)
    if (refreshPromise) return refreshPromise;

    refreshPromise = (async () => {
      try {
        console.log("🔄 API Refresh Request...");
        const res = await fetch(`${BASE_URL}/api/accounts/refresh`, {
          method: 'POST',
          credentials: "include"
        });
        
        if (res.ok) {
          const data = await res.json();
          accessToken.value = data.access_token;
          console.log("💎 Token erneuert");
          return true;
        } else {
           // Wenn Backend "Token Reuse" meldet (401), müssen wir ausloggen
           throw new Error("Refresh abgelehnt (Session ungültig)");
        }
      } catch (e) {
        console.error("Session tot:", e);
        await logout();
        return false;
      } finally {
        refreshPromise = null; // Lock freigeben
      }
    })();

    return refreshPromise;
  };

  // --- AUTH ---
  const checkAuthStatus = async () => {
    isInitialLoading.value = true;
    try {
      // 1. User holen
      const res = await fetch(`${BASE_URL}/api/accounts`, { credentials: "include" });
      if (res.ok) {
        user.value = await res.json();
        
        // 2. Token holen (falls nicht da)
        if (!accessToken.value) {
          await refreshToken();
        }
      } else {
        // Cookie ungültig -> Reset
        user.value = null;
        accessToken.value = null;
      }
    } catch {
       // Netzwerkfehler o.ä.
       user.value = null;
    } finally {
      isInitialLoading.value = false;
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const fd = new URLSearchParams({ username, password });
      const res = await fetch(`${BASE_URL}/api/accounts/login`, {
        method: 'POST',
        headers: { 'Content-Type': "application/x-www-form-urlencoded" },
        credentials: "include",
        body: fd
      });

      if (!res.ok) throw new Error();
      
      const data = await res.json();
      accessToken.value = data.access_token;
      
      await checkAuthStatus();
      startRefreshTimer();
      return true;
    } catch { return false; }
  };

  const logout = async () => {
    if (socket.value) socket.value.close();
    if (refreshTimer) clearInterval(refreshTimer);
    
    await fetch(`${BASE_URL}/api/accounts/logout`, { method: 'POST', credentials: "include" });
    
    user.value = null;
    accessToken.value = null;
    refreshPromise = null;
  };

  // Timer Management
  const startRefreshTimer = () => {
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(() => {
      if (isAuthenticated.value) refreshToken();
    }, 4 * 60 * 1000);
  };

  // Start beim Laden
  startRefreshTimer();

  return { user, accessToken, isAuthenticated, isInitialLoading, checkAuthStatus, connectEngine, login, logout, refreshToken };
});