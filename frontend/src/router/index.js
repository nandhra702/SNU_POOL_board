import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import CreatePoolView from '../views/CreatePoolView.vue'
import PoolDetailsView from '../views/PoolDetailsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/create-pool',
      name: 'create-pool',
      component: CreatePoolView
    },
    {
      path: '/pools/:id',
      name: 'pool-details',
      component: PoolDetailsView
    }
  ]
})

export default router
