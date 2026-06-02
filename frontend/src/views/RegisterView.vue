<script setup>
import { ref } from 'vue' 
import { useRouter } from 'vue-router'

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
            error.value = data.detail || 'Login error' // shows error
        }
    
    } catch(err) {
        error.value = 'Connection error'
    }
}
</script>

<template>
  <div>
    <h1>Register</h1>
    <input id="email" name="email" v-model="email" type="email" autocomplete="email" placeholder="Email" />
    <input id="password" name="password" v-model="password" type="password" autocomplete="new-password" placeholder="Password" />
    <input id="nickname" name="nickname" v-model="nickname" type="text" autocomplete="username" placeholder="Nickname" />
    <p v-if="error">{{ error }}</p>
    <button @click="handleRegister">Register</button>
  </div>
</template>