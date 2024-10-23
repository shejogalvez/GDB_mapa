// Plugins
import { registerPlugins } from '@/plugins'

import './assets/main.css'

import { createApp } from 'vue'
import router from './router/index'
import App from './App.vue'

const app = createApp(App)
registerPlugins(app)

app.use(router)
.mount('#app')
