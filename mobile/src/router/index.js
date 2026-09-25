import { createRouter, createWebHistory } from '@ionic/vue-router'
import { useAuth } from '../composables/useAuth'

import LoginView from '../views/LoginView.vue'
import TabsPage from '../views/TabsPage.vue'
import DashboardTab from '../views/DashboardTab.vue'
import SalesTab from '../views/SalesTab.vue'
import ClientsTab from '../views/ClientsTab.vue'
import ProductsTab from '../views/ProductsTab.vue'
import ProfileTab from '../views/ProfileTab.vue'

const routes = [
  {
    path: '/',
    redirect: '/tabs/dashboard',
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { public: true },
  },
  {
    path: '/tabs/',
    component: TabsPage,
    children: [
      {
        path: '',
        redirect: '/tabs/dashboard',
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: DashboardTab,
      },
      {
        path: 'ventes',
        name: 'ventes',
        component: SalesTab,
      },
      {
        path: 'clients',
        name: 'clients',
        component: ClientsTab,
      },
      {
        path: 'produits',
        name: 'produits',
        component: ProductsTab,
      },
      {
        path: 'profil',
        name: 'profil',
        component: ProfileTab,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuth()

  if (!to.meta.public && !isAuthenticated.value) {
    next({ name: 'login' })
  } else if (to.name === 'login' && isAuthenticated.value) {
    next({ path: '/tabs/dashboard' })
  } else {
    next()
  }
})

export default router
