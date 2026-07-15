import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'
import DashboardView from './views/DashboardView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/login', component: LoginView },
  { path: '/register/student', component: RegisterView, props: { role: 'student' } },
  { path: '/register/company', component: RegisterView, props: { role: 'company' } },
  { path: '/dashboard', component: DashboardView, meta: { login: true } },
]

const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach((to) => to.meta.login && !localStorage.getItem('user') ? '/login' : true)

export default router
