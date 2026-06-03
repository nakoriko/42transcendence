import { createRouter, createWebHistory } from 'vue-router'
import PrivacyPolicy from '../views/PrivacyPolicy.vue'
import TermsOfService from '../views/TermsOfService.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'
import RegisterView from '../views/RegisterView.vue'
import GameView from '../views/GameView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/privacy', component: PrivacyPolicy },
    { path: '/terms', component: TermsOfService },
    { path: '/login', component: LoginView },
    { path: '/profile', component: ProfileView, meta: {requiresAuth: true} },
    { path: '/register', component: RegisterView},
    { path: '/game', component:GameView, meta: {requiresAuth: true} },
  ],
})

router.beforeEach (function(to, from) {
  if(to.meta.requiresAuth && !localStorage.getItem('access')) {
    return '/login'
  }

})

export default router
