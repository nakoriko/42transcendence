<script setup>
import { ref } from 'vue' 
import { useRouter } from 'vue-router'

import AppLogo from '@/components/AppLogo.vue'
import AppCard from '@/components/AppCard.vue'
import AppInput from '@/components/AppInput.vue'
import AppButton from '@/components/AppButton.vue'

const email = ref('')
const password = ref('')
const nickname = ref('')
const error = ref('') //here writes error if something went wrong
const router = useRouter() //needs for redirection after login

async function handleRegister() {
    error.value = '' //reset prevoius error before new request

    try {

        const response = await fetch('/api/users/register/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: email.value, 
                password: password.value,
                nickname: nickname.value
            })
        })

        const data = await response.json() //parse the answer from backend

        if(response.ok) {
            router.push('/login') //redirect to profile
        } else {
            error.value = Object.values(data).flat().join(' ') || 'Registration error' // shows error
        }
    
    } catch(err) {
        error.value = 'Connection error'
    }
}
</script>

<template>

  <div class="min-h-screen bg-navy-900 flex flex-col px-4">
    <div class="pt-8 flex justify-center">
      <AppLogo />
    </div>

    <div class="flex-1 flex flex-col items-center justify-center gap-6 -mt-16">
        <h1 class="page-title">Register</h1>

        <AppCard class="w-full max-w-sm">
            <div class="space-y-4">
            <AppInput v-model="email" label="Email" type="email" placeholder="Email"/>
            <AppInput v-model="password" label="Password" type="password" placeholder="Password"/>
            <AppInput v-model="nickname" label="Nickname" type="text" placeholder="Nickname"/>
            </div>


            <p v-if="error" class="text-coral text-sm mt-3">{{ error }}</p>
            <AppButton class="w-full mt-6" @click="handleRegister">Register</AppButton>

            <p class="secondary-text text-center mt-6">
            Already have an account?
            <RouterLink to="/login" class="link">Login</RouterLink>
            </p>
        </AppCard>
        
    </div>
  </div>
</template>