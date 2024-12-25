import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap'

// Configure axios
const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5000'
axios.defaults.baseURL = backendUrl

// Add auth token to requests if available
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)  // Initialize Pinia before router
app.use(router)

// Make axios available globally
app.config.globalProperties.$axios = axios
app.config.globalProperties.$backendUrl = backendUrl  // Add direct access to backend URL
app.config.globalProperties.$staticUrl = `${backendUrl}/static`  // Ensure proper concatenation

app.mount('#app') 