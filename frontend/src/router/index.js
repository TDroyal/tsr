import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ForcastTaskView from '../views/ForcastTaskView.vue'
import QAView from '../views/QAView.vue'
import AnomalyDetectionTaskView from '../views/AnomalyDetectionTaskView.vue'
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
    path: '/forcast',
    name: 'forcast',
    component: ForcastTaskView
  },
  {
    path: '/anomalydetection',
    name: 'anomalydetection',
    component: AnomalyDetectionTaskView
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
