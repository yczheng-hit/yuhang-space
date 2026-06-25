import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/schedules',
    name: 'Schedules',
    component: () => import('../views/ScheduleView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/recipes',
    name: 'Recipes',
    component: () => import('../views/RecipeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/OrderView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/weights',
    name: 'Weights',
    component: () => import('../views/WeightView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.name === 'Login' || to.name === 'Register') && token) {
    next('/')
  } else {
    next()
  }
})

export default router
