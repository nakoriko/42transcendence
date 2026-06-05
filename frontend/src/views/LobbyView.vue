<script setup>

    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'

    const router = useRouter()
    const user = ref([])
    const error = ref('')
    const selectPlayer2 = ref(null)

    async function fetchUsers() {
        const token = localStorage.getItem('access')
        if(!token) {
            router.push('/login')
        return
    }
    try {
        const response = await fetch('/api/users/list/', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        })
        if(response.ok) {
            const data = await response.json()
            user.value = data
        } else {
            router.push('/login')
        }
    } catch (err) {
        error.value = "Connection error "
    }
}

function startMatch() {
    const opponent = selectPlayer2.value
    if(opponent == null) {
        error.value = "Select an opponent first"
        return
    }
    router.push({ path: '/game', query: { player2: opponent } })
}

onMounted(fetchUsers)

</script>

<template>
    <div>
        <!--- If theres error -->
        <p v-if="error">{{ error }}</p>
        
        <!--- Drop list with players-->
        <select v-model="selectPlayer2">
            <option disabled value="">Choose an opponent</option>
            <option v-for="u in user" :key="u.id" :value="u.id"> 
                {{ u.nickname }}
            </option>
        </select>

        <!--- Button -->
        <button @click="startMatch">Start match</button>
    </div>
</template>