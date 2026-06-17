<script setup>

    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'
    import { apiFetch } from '../utils/apiFetch.js'

    const router = useRouter()
    const friends = ref([])
    const incoming = ref([])
    const allUsers = ref([])
    const error = ref('')


    async function loadData(){
        const token = localStorage.getItem('access')

        if(!token) {
            router.push('/login')
            return
        }
        try {
            const response = await fetch('/api/users/friends/', {
                headers: { 'Authorization': `Bearer ${token}`},
            })
            const data = await response.json()
            if (response.ok) {
                friends.value = data.friends
                incoming.value = data.incoming
            }
        } catch (err) {
            error.value = 'Connection error'
        }

        try {
            const response = await fetch('/api/users/list/', {
                headers: {'Authorization': `Bearer ${token}`},
            })
            const data = await response.json()
            if(response.ok) {
                allUsers.value = data
            }
        } catch {
            error.value = 'Connection error'
        }

    }

    async function sendRequest(userId) {

            const response = await apiFetch('/api/users/friends/request/', {
                method: 'POST',
                body: JSON.stringify({ to_user_id: userId})
            })
            if(response?.ok) //if fetch already return null, we just skip it
                await loadData()
    }

    async function removeFriend(relationId) {
        const response = await apiFetch(`/api/users/friends/${relationId}/`, {
            method: 'DELETE',
        })
        if(response?.ok)
            await loadData()
    }

    async function respondToRequest(relationId, action) {
        const response = await apiFetch(`/api/users/friends/${relationId}/`, {
            method: 'PATCH',
            body: JSON.stringify({ action: action})
        })
        if(response?.ok)
            await loadData()
    }

    onMounted(loadData)


</script>

<template>
    <div> 
        <h1>Friends</h1> 
    </div>
    <div> 
        <h2>My friends</h2>
        <p v-if="friends.length === 0">No friends yet</p>
        <ul v-else>
            <li v-for="relation in friends" :key="relation.id">
                {{ relation.friend.nickname }}
                <span v-if="relation.friend.is_online">🟢</span>
                <span v-else>🔴</span>
                <button @click="removeFriend(relation.id)">Remove</button>
            </li>
        </ul>
    </div>
    <div>
        <h2>Incoming invites</h2>
        <p v-if="incoming.length === 0">No incoming invites yet</p>
        <ul v-else>
            <li v-for="relation in incoming" :key="relation.id">
                {{ relation.friend.nickname }}
                <button @click="respondToRequest(relation.id, 'accept')">✓</button>
                <button @click="respondToRequest(relation.id, 'reject')">✗</button>
            </li>
        </ul>
    </div>
    <div>
        <h2>Invite to play</h2>
        <p v-if="allUsers.length === 0">Oh, there's nobody yet</p>
        <ul v-else>
            <li v-for="user in allUsers" :key="user.id">
                {{ user.nickname }}
                <button @click="sendRequest(user.id)">Invite</button>
            </li>
        </ul>
</div>
</template>