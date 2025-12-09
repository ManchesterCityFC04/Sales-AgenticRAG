import { createApp } from 'vue'
import './style.css'
import './assets/node-update.css'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { useAuthStore } from './stores/auth.js'

const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(ElementPlus)

// 初始化认证状态
const authStore = useAuthStore()
authStore.initAuth()

app.mount('#app')
