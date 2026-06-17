<script setup>
import { ref } from 'vue' 
import { useRouter } from 'vue-router'
import AppLogo from '@/components/AppLogo.vue'
import AppCard from '@/components/AppCard.vue'
import AppInput from '@/components/AppInput.vue'
import AppButton from '@/components/AppButton.vue'


const email = ref('')
const password = ref('')
const error = ref('') //here writes error if something went wrong
const router = useRouter() //needs for redirection after login

async function handleLogin() {
    error.value = '' //reset prevoius error before new request

    try {
        const response = await fetch('/api/users/login/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            email: email.value, 
            password: password.value })
    })

    const data = await response.json() //parse the answer from backend

    if(response.ok) {
        localStorage.setItem('access', data.access) //saves jwt
        localStorage.setItem('refresh', data.refresh) //refresh jwt

        router.push('/profile') //redirect to profile
    } else {
        error.value = data.detail || 'Login error' // shows error
    }
} catch (err) {
    error.value = 'Connection error'
}
    
}
</script>

<template>
  <div class="min-h-screen bg-navy-900 flex flex-col px-4">

    <!-- Лого вверху -->
    <div class="pt-8 flex justify-center">
      <AppLogo />
    </div>

    <!-- Контент по центру -->
    <div class="flex-1 flex flex-col items-center justify-center gap-6 -mt-16">

      <h1 class="page-title">Login</h1>

      <AppCard class="w-full max-w-sm">
        <div class="space-y-4">
          <AppInput
            v-model="email"
            label="Email"
            type="email"
            placeholder="Enter your email"
            autocomplete="email"
          />

            <AppInput
            v-model="password"
            label="Password"
            type="password"
            placeholder="Enter your password"
          />
        </div>

        <p v-if="error" class="text-coral text-sm mt-3">{{ error }}</p>
  
        <AppButton class="w-full mt-6" @click="handleLogin">Login</AppButton>
  
        <p class="secondary-text text-center mt-6">
          No account?
          <RouterLink to="/register" class="link">Register</RouterLink>
        </p>
      </AppCard>
      </div>
    </div>
</template>