<script setup>

import AppButton from '@/components/AppButton.vue'
import AppStatsCard from '@/components/AppStatsCard.vue'
import GameModeCard from '@/components/GameModeCard.vue'
import PlayCard from '@/components/PlayCard.vue'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import LobbyVsRow from '@/components/lobby/LobbyVsRow.vue'
import AppFilterTabs from '@/components/AppFilterTabs.vue'

    const router = useRouter()
    const user = ref([])
    const error = ref('')
    const selectPlayer2 = ref(null)
    const currentUser = ref(null)
    const selectedMode = ref('local')
    const selectedOpponentUser = computed(() =>
        user.value.find(u=>u.id === selectPlayer2.value) ?? null
    )

    // for game modes
    const modeSubtitles = { local: 'Same keyboard', remote: 'Play online' }
    const selectedModeSubtitle = computed(() => modeSubtitles[selectedMode.value] ?? '')

    // for filters
    const activeFilter = ref('All Players')
    const filteredUsers = computed(() =>
        activeFilter.value === 'Friends'
            ? user.value.filter(u => u.is_friend)
            : user.value
    )

    async function fetchUsers() {
        const token = localStorage.getItem('access')
        if(!token) {
            router.push('/login')
        return
    }
    try {
        const profileRes = await fetch('/api/users/profile/', {
            headers: {'Authorization' : `Bearer ` + token}
        })
        if(profileRes.ok) currentUser.value = await profileRes.json()

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

function startMatch() {
    if(!selectedMode.value) {
        error.value = "Sleect a gamr mode first"
    }
    const opponent = selectPlayer2.value
    if(opponent == null) {
        error.value = "Select an opponent first"
        return
    }
    router.push({ path: '/game', query: { player2: opponent, mode:selectedMode.value} })
}

onMounted(fetchUsers)

</script>

<template>
    <div class="min-h-screen px-12 py-14 pb-24 flex flex-col items-center gap-7">

        <div v-if="currentUser" class="w-full max-w-7xl">
            <p class="input-label">Welcome back</p>
            <h1 class="page-title">{{ currentUser.nickname }}</h1>
        </div>

        <div class="grid grid-cols-[2fr_1fr] gap-16 w-full max-w-7xl mt-10">

            <!-- Левая колонка: режим + оппоненты -->
            <div class="flex flex-col gap-8">

                <!-- Режим -->
                <div class="flex flex-col gap-3">
                    <span class="input-label">Choose game mode</span>
                    <div class="flex items-center gap-3">
                        <GameModeCard title="Local"
                            :selected="selectedMode === 'local'"
                            @select="tooggleMode('local')" />
                        <GameModeCard title="Remote"
                            :selected="selectedMode === 'remote'"
                            @select="tooggleMode('remote')" />
                        <GameModeCard title="vs AI" :disabled="true" />
                        <span v-if="selectedModeSubtitle"
                            class="text-base font-light text-muted/50 ml-auto">
                            {{ selectedModeSubtitle }}
                        </span>
                    </div>
                </div>

                <!-- Оппоненты -->
                <div class="flex flex-col gap-3">
                    <div class="border-t border-white/[0.07] pb-3 pt-8 flex items-center justify-between">
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
                v-if="currentUser"
                :currentUser="currentUser"
                :opponent="selectedOpponentUser">
                <p v-if="error" class="text-xs text-coral mt-1">{{ error }}</p>
                <AppButton variant="compact" @click="startMatch">Start game</AppButton>
            </LobbyVsRow>

        </div>
    </div>
</template>