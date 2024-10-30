// Plugins
import { registerPlugins } from '@/plugins'

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router/index'
import App from './App.vue'

const app = createApp(App)
registerPlugins(app)

app.use(router)
.use(createPinia())
.mount('#app')
