<script setup>
import AppAvatar from '@/components/AppAvatar.vue'
import { ref, onMounted } from 'vue' 
import { useRouter } from 'vue-router'

const user = ref(null)
const error = ref('')
const router = useRouter()
const selectedFile = ref(null)

//AVATAR
async function handleFileSelect(event) {
    selectedFile.value = event.target.files[0] //saves selected file inside variable
    await uploadAvatar()
}

//upload
async function uploadAvatar() {
    if(!selectedFile.value) return

    const formData = new FormData()
    formData.append('avatar', selectedFile.value)

    const token = localStorage.getItem('access')
    const response = await fetch('/api/users/avatar/', {
        method: 'PATCH', //updates user tha already exist
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData

    })

    if(response.ok)
        await loadProfile()
}



//async function tu use await
async function loadProfile() {
    const token = localStorage.getItem('access')

    if(!token) {
        router.push('/login')
        return
    }
    try {
        const response = await fetch('/api/users/profile/', {
            headers: { 'Authorization': `Bearer ${token}`},
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


onMounted(loadProfile)

</script>

<template>
    <div class="min-h-screen bg-navy-900">
        <div v-if="user">
            <h1>Profile</h1>
            <img v-if="user.avatar"
                :src="user.avatar" alt="avatar" width="100">
            <AppAvatar v-else :nickname="user.nickname"></AppAvatar>
            <input type="file" accept="image/*" @change="handleFileSelect">
            <!-- <button @click="uploadAvatar">Upload avatar</button> -->
            <p>Email: {{ user.email }}</p>
            <p>Nickname: {{ user.nickname }}</p>
            <p>Wins: {{ user.wins ?? 0 }}</p>
            <p>Losses {{ user.losses ?? 0 }}</p>
            <!-- <button @click="logout">Logout</button> -->
        </div>
        <div v-else-if="error">{{ error }}</div>
        <div v-else>Loading...</div>
    </div>
</template>