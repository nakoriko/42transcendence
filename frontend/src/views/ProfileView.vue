<script setup>
import ProfileStatsCard from '@/components/ProfileStatsCard.vue'
import RecentMatchesList from '@/components/RecentMatchesList.vue'
import { ref, onMounted, computed } from 'vue' 
import { apiFetch } from '@/utils/apiFetch'
import ProfileFriendsBlock from '@/components/profile/ProfileFriendsBlock.vue'
import ProfileInfoCard from '@/components/profile/ProfileInfoCard.vue'

const user = ref(null)
const error = ref('')
const matches = ref([])

//for filters:
const activeFilter = ref('all')
const filteredMatches = computed(() => {
    if(activeFilter.value === 'wins') return matches.value.filter(m => m.result === 'win')
    if(activeFilter.value === 'losses') return matches.value.filter(m => m.result === 'loss')
    return matches.value

})

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
    <div class="pb-16">
        <div v-if="error" class="text-coral text-sm"> {{ error }}</div>
        <div v-if="user">
            <p class="input-label mb-1">Transcend · Player info</p>
            <h1 class="page-title">Profile page </h1>
            <div class="mb-8 border-b border-white/[0.07] pb-8">
                    <ProfileInfoCard class="mt-8"  :user="user" @updated="loadProfile" />
                    <ProfileStatsCard class="mt-6" :wins="user.wins ?? 0" :losses="user.losses ?? 0"></ProfileStatsCard>
            </div>
            
            <!--Stats card-->
            <div class="grid  grid-cols-1 lg:grid-cols-[2fr_1fr] gap-8 lg:gap-10 ">
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