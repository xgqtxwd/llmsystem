import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/health-profile',
    name: 'HealthProfile',
    component: () => import('@/views/HealthProfile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/diet-preferences',
    name: 'DietPreferences',
    component: () => import('@/views/DietPreferences.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/health-goals',
    name: 'HealthGoals',
    component: () => import('@/views/HealthGoals.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/recipes',
    name: 'Recipes',
    component: () => import('@/views/Recipes.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('@/views/Knowledge.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge-list',
    name: 'KnowledgeList',
    component: () => import('@/views/KnowledgeList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function isAuthenticated() {
  return !!localStorage.getItem('token')
}

function isAdmin() {
  return localStorage.getItem('is_admin') === 'true'
}

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated()) {
    next('/home')
  } else if (to.meta.requiresAdmin && !isAdmin()) {
    next('/home')
  } else {
    next()
  }
})

export default router
