import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ProductsView from '../views/ProductsView.vue'
import ClientsView from '../views/ClientsView.vue'
import SalesView from '../views/SalesView.vue'
import PaymentMethodsView from '../views/PaymentMethodsView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { public: true },
  },
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
  },
  {
    path: '/produits',
    name: 'produits',
    component: ProductsView,
  },
  {
    path: '/clients',
    name: 'clients',
    component: ClientsView,
  },
  {
    path: '/ventes',
    name: 'ventes',
    component: SalesView,
  },
  {
    path: '/paiements',
    name: 'paiements',
    component: PaymentMethodsView,
  },
  {
    path: '/profil',
    name: 'profil',
    component: ProfileView,
  },
]

const isFileProtocol = typeof window !== 'undefined' && window.location.protocol === 'file:'
const router = createRouter({
  history: isFileProtocol ? createWebHashHistory() : createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuth()

  if (!to.meta.public && !isAuthenticated.value) {
    next({ name: 'login' })
  } else if (to.name === 'login' && isAuthenticated.value) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
