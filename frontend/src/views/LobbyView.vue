<script setup>

import AppButton from '@/components/AppButton.vue'
import { apiFetch } from '@/utils/apiFetch'
import GameModeCard from '@/components/GameModeCard.vue'
import PlayCard from '@/components/PlayCard.vue'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import LobbyVsRow from '@/components/lobby/LobbyVsRow.vue'
import AppFilterTabs from '@/components/AppFilterTabs.vue'
import { usePresenceStore } from '@/stores/presence'


    const userStore = useUserStore()
    const presenceStore = usePresenceStore()
    const router = useRouter()
    const user = ref([])
    const error = ref('')
    const selectPlayer2 = ref(null)
    const selectedMode = ref('local')

    
    //for live presence
    const liveUsers = computed(() =>
        user.value.map(u => ({
            ...u,
            is_online: presenceStore.online[u.id] ?? u.is_online
        }))
    )


    const selectedOpponentUser = computed(() =>
        liveUsers.value.find(u=>u.id === selectPlayer2.value) ?? null
    )


    // for game modes
    const modeSubtitles = { local: 'Same keyboard', remote: 'Play online' }
    const selectedModeSubtitle = computed(() => modeSubtitles[selectedMode.value] ?? '')

    // for filters
    const activeFilter = ref('All Players')
    const filteredUsers = computed(() =>
        activeFilter.value === 'Friends'
            ? liveUsers.value.filter(u => u.is_friend)
            : liveUsers.value
    )


    async function fetchUsers() {
    try {
        const response = await apiFetch('/api/users/list/')
        if(!response) return
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

function toogglePlayer(id) {
    if(selectPlayer2.value == id) {
        selectPlayer2.value = null
    } else {
        selectPlayer2.value = id
        error.value = ''
    }
}

function tooggleMode(mode) {
    selectedMode.value = mode
}

async function startMatch() {
    if(!selectedMode.value) {
        error.value = "Sleect a gamr mode first"
        return
    }
    const opponent = selectPlayer2.value
    if(opponent == null) {
        error.value = "Select an opponent first"
        return
    }
    if(selectedMode.value === 'local') {
        router.push({ path: '/game', query: { player2: opponent, mode:selectedMode.value} })
        return
    }

    const res = await apiFetch('/api/game/matches/invite/', {
        method: 'POST',
        body: JSON.stringify({ opponent_id: opponent })
    })
    if(!res || !res.ok) {
        error.value = "Failed to create match"
        return
    }
    const data = await res.json()
    router.push ({ path: '/game/remote', query: { player2: opponent, match_id: data.id }})
}

onMounted(fetchUsers)

</script>

<template>
    <div class="pb-16 flex flex-col items-center gap-7">

        <div v-if="userStore.currentUser" class="w-full max-w-7xl">
            <p class="input-label">Welcome back</p>
            <h1 class="page-title">{{ userStore.currentUser.nickname }}</h1>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[2fr_1fr] items-center gap-8 lg:gap-16 w-full max-w-7xl mt-10">

            <!-- Левая колонка: режим + оппоненты -->
            <div class="flex flex-col gap-8">

                <!-- Режим -->
                <div class="flex flex-col gap-3">
                    <span class="input-label">Choose game mode</span>
                    <div class="flex items-center gap-3 flex-wrap">
                        <GameModeCard title="Local"
                            :selected="selectedMode === 'local'"
                            @select="tooggleMode('local')" />
                        <GameModeCard title="Remote"
                            :selected="selectedMode === 'remote'"
                            @select="tooggleMode('remote')" />
                        <GameModeCard title="vs AI" :disabled="true" />
                        <span v-if="selectedModeSubtitle"
                            class="text-base font-light text-muted/50 sm:ml-auto">
                            {{ selectedModeSubtitle }}
                        </span>
                    </div>
                </div>

                <!-- Оппоненты -->
                <div class="flex flex-col gap-3">
                    <div class="border-t border-white/[0.07] pb-3 pt-8 flex items-center justify-between flex-wrap gap-3">
                        <span class="input-label">Choose an opponent</span>
                        <AppFilterTabs :options="['All Players', 'Friends']" v-model="activeFilter" />
                    </div>
                    <div class="flex flex-col overflow-y-auto max-h-[420px] scroll-thin">
                        <PlayCard v-for="u in filteredUsers"
                            :key="u.id"
                            :user="u"
                            :selected="selectPlayer2 === u.id"
                            @select="toogglePlayer($event)" />
                    </div>
                </div>

            </div>

            <!-- Правая колонка: матч -->
            <LobbyVsRow
                v-if="userStore.currentUser"
                :currentUser="userStore.currentUser"
                :opponent="selectedOpponentUser">
                <p v-if="error" class="text-xs text-coral mt-1">{{ error }}</p>
                <AppButton variant="compact" @click="startMatch">Start game</AppButton>
            </LobbyVsRow>

        </div>
    </div>
</template>