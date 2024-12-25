import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Import Bootstrap and its styles
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import * as bootstrap from 'bootstrap'

// Import our custom styles
import './assets/styles/main.scss'

// Configure axios
axios.defaults.baseURL = ''
axios.defaults.withCredentials = true
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Make bootstrap available globally
window.bootstrap = bootstrap

app.mount('#app') 