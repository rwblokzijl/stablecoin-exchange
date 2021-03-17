import Vue from 'vue'
import App from './App.vue'

import VueCookies from 'vue-cookies'
import VueQrcode from '@chenfengyuan/vue-qrcode'
import VModal from 'vue-js-modal'

Vue.use(VueCookies)
Vue.use(VModal)

Vue.component(VueQrcode.name, VueQrcode)

Vue.config.productionTip = false

new Vue({
  render: h => h(App)
}).$mount('#app')
