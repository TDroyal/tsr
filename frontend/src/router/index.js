import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import TaskView from '../views/TaskView.vue'
import QAView from '../views/QAView'
const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginView
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView
  },
  {
    path: '/task',
    name: 'task',
    component: TaskView
  },
  {
    path: '/chat',
    name: 'chat',
    component: QAView
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
