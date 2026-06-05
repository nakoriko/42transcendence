<script setup>
import { ref, onMounted } from 'vue' 
import { useRouter } from 'vue-router'

const user = ref(null)
const error = ref('')
const router = useRouter()

//async function tu use await
async function loadProfile() {
    const token = localStorage.getItem('access')

    if(!token) {
        router.push('/login')
        return
    }
    try {
        const response = await fetch('/api/users/profile/', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        })
        if(response.ok) {
            user.value = await response.json()
        } else {
            router.push('/login')
        }
    } catch (err) {
        error.value = 'Connection error'
    }
}

function logout() {
    localStorage.removeItem('access')
    router.push('/login')
}
onMounted(loadProfile)

</script>

<template>
    <div v-if="user">
        <h1>Profile</h1>
        <p>Email: {{ user.email }}</p>
        <p>Nickname: {{ user.nickname }}</p>
        <p>Wins: {{ user.wins ?? 0 }}</p>
        <p>Losses {{ user.losses ?? 0 }}</p>
        <button @click="logout">Logout</button>
    </div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>Loading...</div>
</template>