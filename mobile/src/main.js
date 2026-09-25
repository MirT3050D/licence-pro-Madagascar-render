import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { IonicVue } from '@ionic/vue'

/* Theme variables and Ionic CSS */
import './theme/variables.css'

const app = createApp(App)
  .use(IonicVue, {
    mode: 'ios',
    animated: true,
  })
  .use(router)

router.isReady().then(() => {
  app.mount('#app')
})
