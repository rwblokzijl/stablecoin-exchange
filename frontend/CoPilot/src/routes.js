import DashView from './components/Dash.vue'
import LoginView from './components/Login.vue'
import NotFoundView from './components/404.vue'

// Import Views - Dash
import DashboardView from './components/views/Dashboard.vue'

import AccountView from './components/views/user/Account.vue'
import TransactionsView from './components/views/user/Transactions.vue'
import ExchangeView from './components/views/user/Exchange.vue'

import BankDashView from './components/views/bank/Dashboard.vue'
import PolicyView from './components/views/bank/Policy.vue'
import BankStatsView from './components/views/bank/Statistics.vue'

import RegulatorDashView from './components/views/regulator/Dashboard.vue'
import CasesView from './components/views/regulator/Cases.vue'

import NotaryDashView from './components/views/notary/Dashboard.vue'
import RequestsView from './components/views/notary/Requests.vue'
import NotaryStatsView from './components/views/notary/Statistics.vue'

// Routes
const routes = [
  {
    path: '/login',
    component: LoginView
  },
  {
    path: '/',
    component: DashView,
    children: [
      {
        path: 'dashboard',
        alias: '',
        component: DashboardView,
        name: 'Dashboard',
        meta: {description: 'Overview of environment'}
      }, {
        path: 'account',
        component: AccountView,
        name: 'Wallet',
        meta: {description: 'User wallet'}
      }, {
        path: 'transactions',
        component: TransactionsView,
        name: 'Transactions',
        meta: {description: 'User transactions'}
      }, {
        path: 'exchange',
        component: ExchangeView,
        name: 'Exchange',
        meta: {description: 'Exchange'}
      }, {
        path: 'bank',
        component: BankDashView,
        name: 'Dashboard',
        meta: {description: 'Overview of activities'}
      }, {
        path: 'bank/policy',
        component: PolicyView,
        name: 'Settings and Policy',
        meta: {description: 'Bank policy and configurations'}
      }, {
        path: 'bank/statistics',
        component: BankStatsView,
        name: 'Statistics',
        meta: {description: 'Simple and advance table in CoPilot'}
      }, {
        path: 'regulator',
        component: RegulatorDashView,
        name: 'Dashboard',
        meta: {description: 'Simple and advance table in CoPilot'}
      }, {
        path: 'regulator/cases',
        component: CasesView,
        name: 'Cases',
        meta: {description: 'Simple and advance table in CoPilot'}
      }, {
        path: 'notary',
        component: NotaryDashView,
        name: 'Dashboard',
        meta: {description: 'Simple and advance table in CoPilot'}
      }, {
        path: 'notary/requests',
        component: RequestsView,
        name: 'Requests',
        meta: {description: 'Simple and advance table in CoPilot'}
      }, {
        path: 'notary/statistics',
        component: NotaryStatsView,
        name: 'Statistics',
        meta: {description: 'Simple and advance table in CoPilot'}
      }
    ]
  }, {
    // not found handler
    path: '*',
    component: NotFoundView
  }
]

export default routes
