<script setup>
import { ref } from 'vue' 
import { useRouter } from 'vue-router'

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
  <div>
    <h1>Login</h1>
    <input id="email" name="email" v-model="email" type="email" autocomplete="email" placeholder="Email" />
    <input id="password" name="password" v-model="password" type="password" autocomplete="current-password" placeholder="Password" />
    <p v-if="error">{{ error }}</p>
    <button @click="handleLogin">Login</button>
    <p>No account? <RouterLink to='/register'>Register</RouterLink></p>
  </div>
</template>