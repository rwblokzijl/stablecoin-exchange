// import DashView from './components/Dash.vue'
import NotFoundView from './components/404.vue'

import ExchangeView from './components/views/user/Exchange.vue'
// Routes
const routes = [
  {
    path: '/',
    component: ExchangeView,
    name: 'Exchange',
    meta: { description: 'Exchange' }
  }, {
    // not found handler
    path: '*',
    component: NotFoundView
  }
]

export default routes
