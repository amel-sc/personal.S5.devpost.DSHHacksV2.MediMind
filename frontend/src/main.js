import './assets/bootstrap/css/bootstrap.min.css'
import './assets/bootstrap/js/bootstrap.bundle.min.js'
import './assets/bootstrap/icons/bootstrap-icons.css'
import './assets/global.css'
import router from './router'
import { i18n } from './i18n'

import { createApp } from 'vue'
import App from './App.vue'

createApp(App).use(i18n).use(router).mount('#app')