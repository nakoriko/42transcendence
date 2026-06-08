<script setup>
import { ref } from 'vue' 
import { useRouter } from 'vue-router'
import AppLogo from '@/components/AppLogo.vue'


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
    <div class="flex-1 flex flex-col items-center justify-center gap-6">

      <h1 class="text-3xl font-light text-white">Login</h1>

      <div class="bg-navy-800 border border-white/[0.07] rounded-[16px] p-10 w-full max-w-sm">

        <div class="space-y-4">
          <div>
            <label class="block text-xs text-muted mb-1 uppercase tracking-widest">Email</label>
            <input v-model="email" type="email" placeholder="Enter your email"
              class="w-full bg-navy-900 border border-white/[0.07] rounded-xl px-4 py-3 text-white placeholder:text-muted/50 focus:outline-none focus:border-teal/50 transition" />
          </div>
          <div>
            <label class="block text-xs text-muted mb-1 uppercase tracking-widest">Password</label>
            <input v-model="password" type="password" placeholder="Enter your password"
              class="w-full bg-navy-900 border border-white/[0.07] rounded-xl px-4 py-3 text-white placeholder:text-muted/50 focus:outline-none focus:border-teal/50 transition" />
          </div>
        </div>

        <p v-if="error" class="text-coral text-sm mt-3">{{ error }}</p>

        <button @click="handleLogin"
          class="w-full mt-6 border border-teal text-teal py-3 rounded-[50px] hover:bg-sage hover:border-transparent hover:text-navy-900 transition">
          Login
        </button>

        <p class="text-center text-muted text-sm mt-6">
          No account?
          <RouterLink to="/register" class="text-teal hover:text-sand transition">Register</RouterLink>
        </p>

      </div>
    </div>

  </div>
</template>