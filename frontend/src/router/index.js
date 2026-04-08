import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
    { path: '/register', name: 'register', component: () => import('../views/Register.vue') },
    { 
      path: '/orders', 
      name: 'orders', 
      component: () => import('../views/Orders.vue'),
      meta: { requiresAuth: true } // 标记需要登录
    }
  ]
})

// 路由守卫：检查是否登录
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token') || localStorage.getItem('session_id')
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
