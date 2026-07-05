
<script setup>
import { apiFetch } from '@/utils/apiFetch'
import { ref, onMounted, computed } from 'vue'
import PlayCard from '../PlayCard.vue'
import AppFilterTabs from '../AppFilterTabs.vue'
import { X } from 'lucide-vue-next'
    const friends=ref([])
    const outgoing=ref([])
    const incoming=ref([])

    const allUsers=ref([])
    const showDropdown= ref(false)
    const selectedId = ref(null)
    const activeFilter = ref('all')

    const filteredList = computed(() => {
        if(activeFilter.value === 'pending') return outgoing.value
        if(activeFilter.value === 'online') return friends.value.filter(f => f.friend.is_online)
        return friends.value
    })

    async function loadFriends() {
        const res = await apiFetch(`/api/users/friends/`)
        if (!res?.ok) return
        const data = await res.json()
        friends.value = data.friends ?? []
        outgoing.value = data.outgoing ?? []
        incoming.value = data.incoming ?? []
        
    }

    async function removeFriend(relationId) {
        const res = await apiFetch(`/api/users/friends/${relationId}/`, { method: 'DELETE'})
        if(res?.ok) {
            allUsers.value = []
            await loadFriends()
        }

    }

    async function sendRequest(userID) {
        const res = await apiFetch(`/api/users/friends/request/`, {
            method: 'POST',
            body: JSON.stringify({ to_user_id: userID })
        })
        if(res?.ok) {
            showDropdown.value = false
            allUsers.value = []
            await loadFriends()
        }
    }

    const availableUsers = computed(() => {
        const friendIds = friends.value.map(f => f.friend.id)
        const outgoingIds = outgoing.value.map (f => f.friend.id)
        const incomingIds = incoming.value.map(f => f.friend.id)

        return allUsers.value.filter ( u =>
            !friendIds.includes(u.id) &&
            !outgoingIds.includes(u.id) &&
            !incomingIds.includes(u.id) && 
            !u.is_friend
        )
    })

    async function toggleDropdown() {

        showDropdown.value = !showDropdown.value
        if (showDropdown.value && allUsers.value.length === 0 ) {
                const res = await apiFetch('/api/users/list/')
                if(!res?.ok) return
                allUsers.value = await res.json()
            }
    }

    onMounted(() => {
        loadFriends()
        window.addEventListener('friends-updated', loadFriends)
    })

</script>

<template>
    <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
            <span class="input-label">Friends</span>
            <div class="flex items-center gap-2">
                <AppFilterTabs
                    :options="['all', 'online', 'pending']"
                    :modelValue="activeFilter"
                    @update:modelValue="activeFilter = $event" />
                <button @click="toggleDropdown"
                class="w-7 h-7 rounded-md bg-white/[0.04] hover:bg-white/[0.08]
                            text-muted hover:text-white transition
                            flex items-center justify-center text-base leading-none">
                    +
                </button>
            </div>
        </div>
        <div v-if="showDropdown" class="flex flex-col gap-1 mb-1">
            <div v-for="u in availableUsers" :key="u.id"
                class="flex items-center gap-3 px-3 py-2 rounded-xl
                    bg-white/[0.02] hover:bg-white/[0.04] transition">
                <span class="text-sm text-white flex-1">{{ u.nickname }}</span>
                <button @click="sendRequest(u.id)"
                    class="text-[10px] text-teal bg-teal/10 rounded px-2 py-0.5 hover:bg-teal/20 transition">
                    Add friend
                </button>
            </div>
        </div>
        <div class="flex flex-col overflow-y-auto max-h-[420px] scroll-thin gap-1">
            <div v-if="filteredList.length === 0" class="text-[11px] text-muted py-2">
                No friends here yet
            </div>
            <!-- карточки сюда -->
             <div v-for="f in filteredList" :key="f.id"
                class="flex items-center gap-2">
                <div class="flex-1 min-w-0" @click="selectedId = selectedId === f.id ? null : f.id">
                    <PlayCard :user="f.friend" :selected="selectedId === f.id" />
                </div>
                <button v-if="selectedId === f.id"
                    @click="removeFriend(f.id); selectedId = null"
                    class="flex-shrink-0 p-1.5 rounded-md text-coral hover:bg-coral/10 transition">
                    <X :size="13" />
                </button>
            </div>
        </div>
    </div>
</template>