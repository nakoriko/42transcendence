<script setup>
import ProfileAvatar from '@/components/ProfileAvatar.vue'
import ProfileStatsCard from '@/components/ProfileStatsCard.vue'
import RecentMatchesList from '@/components/RecentMatchesList.vue'
import { ref, onMounted, computed } from 'vue' 
import { apiFetch } from '@/utils/apiFetch'
import AppInput from '@/components/AppInput.vue'
import AppButton from '@/components/AppButton.vue'
import ProfileFriendsBlock from '@/components/profile/ProfileFriendsBlock.vue'

const user = ref(null)
const error = ref('')
const matches = ref([])
const isEditing = ref(false)
const editForm = ref({ nickname: '', email: '' })

//for filters:
const activeFilter = ref('all')
const filteredMatches = computed(() => {
    console.log('result values:', matches.value.map(m => m.result))
    if(activeFilter.value === 'wins') return matches.value.filter(m => m.result === 'win')
    if(activeFilter.value === 'losses') return matches.value.filter(m => m.result === 'loss')
    return matches.value

})



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
        const response = await apiFetch('/api/game/matches/?limit=5')
        if(!response) return
        if(!response.ok) { matches.value = []; return}
        const data = await response.json()
        matches.value = data.results ?? data
    } catch (err) {
        error.value = 'Connection error'
    }
}

onMounted(async() => {
    await Promise.all([loadProfile(), loadMatches()])
})

</script>

<template>
    <div>
        <div v-if="error" class="text-coral text-sm"> {{ error }}</div>
        <div v-if="user">
            <div class="flex items-center justify-between mb-6">
                <h1 class="page-title">Profile</h1>
                <span class="text-[10px] text-muted">@{{ user.nickname }}</span>
            </div>


            <div class="grid grid-cols-[2fr_1fr] gap-6 ">

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
                <RecentMatchesList 
                    :matches="filteredMatches"
                    :activeFilter="activeFilter"
                    @filter-change="activeFilter = $event">
                </RecentMatchesList>

                <!--Friends preview-->
                <!--Friends-->
                <ProfileFriendsBlock />
            </div>

        </div>
        <div v-else class="text-muted text-sm">Loading...</div>
    </div>
</template>