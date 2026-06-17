<script setup>
import AppAvatar from '@/components/AppAvatar.vue'
import ProfileAvatar from '@/components/ProfileAvatar.vue'
import ProfileStatsCard from '@/components/ProfileStatsCard.vue'
import RecentMatchesList from '@/components/RecentMatchesList.vue'
import { ref, onMounted, computed } from 'vue' 
import { RouterLink, useRouter } from 'vue-router'
import { apiFetch } from '@/utils/apiFetch'
import AppInput from '@/components/AppInput.vue'
import AppButton from '@/components/AppButton.vue'

const user = ref(null)
const error = ref('')
const friends = ref([])
const matches = ref([])
const isEditing = ref(false)
const editForm = ref({ nickname: '', email: '' })


//editing
function startEditing() {
    editForm.value.nickname = user.value.nickname
    editForm.value.email = user.value.email
    isEditing.value = true
}

//save changes
async function saveProfile() {
    const response = await apiFetch('/api/users/profile/', {
        method: 'PATCH',
        body: JSON.stringify({
            nickname: editForm.value.nickname,
            email: editForm.value.email
        })
    })
    if(response?.ok) {
        await loadProfile()
        isEditing.value = false
    }
}

//upload
async function uploadAvatar(file) {
    if(!file) return

    const formData = new FormData()
    formData.append('avatar', file)

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
    try {
        const response = await apiFetch('/api/users/profile/')
        if(!response) return
        if(!response.ok) { error.value = 'Failed to load profile'; return}
        user.value = await response.json()
    } catch (err) {
        error.value = 'Connection error'
    }
}


async function loadMatches() {
    try {
        const response = await apiFetch('/api/game/matches/?limit=3')
        if(!response) return
        if(!response.ok) { matches.value = []; return}
        const data = await response.json()
        matches.value = data.results ?? data
    } catch (err) {
        error.value = 'Connection error'
    }
}

async function loadFriends() {
    try {
        const response = await apiFetch('/api/users/friends/')
        if(!response) return
        if(!response.ok) { friends.value = []; return}
        const data = await response.json()
        friends.value = data.friends ?? data
    } catch (err) {
        error.value = 'Connection error'
    }
}


onMounted(async() => {
    await Promise.all([loadProfile(), loadFriends(), loadMatches()])
})

</script>

<template>
    <div class="px-10 py-10">
        <div v-if="error" class="text-coral text-sm"> {{ error }}</div>
        <div v-if="user">
            <div class="flex items-center justify-between mb-6">
                <h1 class="page-title">Profile</h1>
                <span class="text-[10px] text-muted">@{{ user.nickname }}</span>
            </div>

            <div class="grid grid-cols-[1fr_240px] gap-4">

                <!--Profile card-->
                <div class="card">
                    <div class="flex items-center justify-between mb-3">
                        <span class="input-label">Your info</span>
                        <button v-if="!isEditing"
                            @click="startEditing"
                            class="text-xs text-teal bg-teal/10 rounded-md px-2 py-0.5 hover:bg-teal/20 transition">edit</button>
                    </div>
                    <ProfileAvatar
                    :user="user"
                    :canUpload="true"
                    @upload="uploadAvatar">
                    </ProfileAvatar>
                
                <div v-if="isEditing" class="mt-4 flex flex-col gap-3">
                    <AppInput v-model="editForm.nickname" label="Nickname" type="text"></AppInput>
                    <AppInput v-model="editForm.email" label="Email" type="email"></AppInput>
                    <div class="flex gap-2 mt-1">
                        <AppButton variant="primary" @click="saveProfile">Save</AppButton>
                        <AppButton variant="ghost" @click="isEditing = false">Cancel</AppButton>
                    </div>
                </div>


                </div>

                <!--Stats card-->
                <ProfileStatsCard :wins="user.wins ?? 0" :losses="user.losses ?? 0"></ProfileStatsCard>

                <!--recent matches-->
                <RecentMatchesList :matches="matches"></RecentMatchesList>

                <!--Friends preview-->
                <div class="card">
                    <div class="card-label">Friends</div>
                    <div class="flex flex-col gap-2">
                        <div v-for="f in friends.slice(0, 3)" :key="f.id"
                            class="flex items-center gap-2">
                            <AppAvatar :nickname="f.friend.nickname" :isOnline="f.friend.is_online"></AppAvatar>
                            <div class="text-[11px] text-white">{{ f.friend.nickname }}</div>
                            <div class="text-[9px]" :class="f.friend.is_online ? 'text-green-400' : 'text-muted'">
                                {{ f.friend.is_online ? 'online' : 'offline' }}
                            </div>
                        </div>
                        <RouterLink to="/friends"
                            class="text-[10px] text-teal mt-3 flex items-center gap-1">See all friends</RouterLink>
                    </div>
                </div>
            </div>

        </div>
        <div v-else class="text-muted text-sm">Loading...</div>
    </div>
</template>