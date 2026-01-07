import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router' // 1. Router importieren
import App from './App.vue'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router) // 2. Router verwenden

app.mount('#app')