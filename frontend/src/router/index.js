import { createRouter, createWebHistory } from 'vue-router'
import PrivacyPolicy from '../views/PrivacyPolicy.vue'
import TermsOfService from '../views/TermsOfService.vue'



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/privacy', component: PrivacyPolicy },
    { path: '/terms', component: TermsOfService },
  ],
})

export default router
