<script setup>
import { ref } from 'vue' 
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AppLogo from '@/components/AppLogo.vue'
import AppCard from '@/components/AppCard.vue'
import AppInput from '@/components/AppInput.vue'
import AppButton from '@/components/AppButton.vue'

const userStore = useUserStore()
const email = ref('')
const password = ref('')
const error = ref('') //here writes error if something went wrong
const router = useRouter() //needs for redirection after login

async function handleLogin() {
    error.value = '' //reset prevoius error before new request
    const result = await userStore.login(email.value, password.value)
    if (result.success) router.push('/profile')
    else error.value = result.error
}
</script>

<template>
  <div class="min-h-screen bg-navy-900 flex flex-col px-4">
    <div class="pt-8 flex justify-center"><AppLogo /></div>
    <div class="flex-1 flex flex-col items-center justify-center gap-6 -mt-16">
      <h1 class="page-title">Login</h1>
      <AppCard class="w-full max-w-sm">
        <div class="space-y-4">
          <AppInput v-model="email" label="Email" type="email" placeholder="Enter your email" autocomplete="email"/>
          <AppInput v-model="password" label="Password" type="password" placeholder="Enter your password"/>
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