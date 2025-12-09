import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import Login from '../views/Login.vue'
import Chat from '../views/Chat.vue'
import History from '../views/History.vue'
import DocumentLibrary from '../views/DocumentLibrary.vue'
import KnowledgeGraph from '../views/KnowledgeGraph.vue'
import Demo from '../views/Demo.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/chat'
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/chat',
      name: 'chat',
      component: Chat,
      meta: { requiresAuth: true }
    },
    {
      path: '/history',
      name: 'history',
      component: History,
      meta: { requiresAuth: true }
    },
    {
      path: '/document-library',
      name: 'document-library',
      component: DocumentLibrary,
      meta: { requiresAuth: true }
    },
    {
      path: '/knowledge-graph/:collection_id',
      name: 'knowledge-graph',
      component: KnowledgeGraph,
      meta: { requiresAuth: true }
    },
    {
      path: '/demo',
      name: 'demo',
      component: Demo
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    if (authStore.isAuthenticated) {
      next()
    } else {
      next('/login')
    }
  } else {
    // 如果已经登录且访问登录页，重定向到聊天页
    if (to.name === 'login' && authStore.isAuthenticated) {
      next('/chat')
    } else {
      next()
    }
  }
})

export default router