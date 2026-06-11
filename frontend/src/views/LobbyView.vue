<script setup>

    import AppButton from '@/components/AppButton.vue'
import AppStatsCard from '@/components/AppStatsCard.vue'
import GameModeCard from '@/components/GameModeCard.vue'
import PlayCard from '@/components/PlayCard.vue'
import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'

    const router = useRouter()
    const user = ref([])
    const error = ref('')
    const selectPlayer2 = ref(null)
    const currentUser = ref(null)
    const selectedMode = ref(null) // add after mode variable for 'local' | 'ai' | 'remote'

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
    if(selectedMode.value == mode) {
        selectedMode.value = null
    } else {
        selectedMode.value = mode
    }
}

function startMatch() {
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
    <div class="min-h-screen px-12 py-14 pb-24" >
        <div v-if="currentUser" class="lg:w-80 mb-8"> <!--protection while assync fetchUsers finish his a request-->
            <h1 class="page-title">Welcome back, <br>{{ currentUser.nickname }}</h1>
        </div>

        <div class="flex flex-col lg:flex-row gap-8 w-full items-start">

            <!--Left column-->
            <div class="flex flex-col gap-5 lg:w-80 w-full flex-shrink-0">
                <div v-if="currentUser" class="flex flex-col gap-2"> <!--protection while assync fetchUsers finish his a request-->
                    <span class="input-label">Your stats</span>
                    <AppStatsCard :wins="currentUser.wins" :losses="currentUser.losses"></AppStatsCard>
                </div>

                
                <div class="flex flex-col gap-3">
                    <span class="input-label">Choose game mode</span>
                    <GameModeCard icon="🎮" title="Local" subtitle="Same keyboard"
                    :selected="selectedMode === 'local'"
                    @select="tooggleMode('local')"></GameModeCard>
                    <GameModeCard icon="🎮" title="vs AI"  :disabled="true" ></GameModeCard>
                    <GameModeCard icon="🌐" title="Remote"  :disabled="true" ></GameModeCard>
                </div>
                

                <p v-if="error" class="text-xs text-coral text-center">{{ error }}</p>
            </div>


            <!--- Right columnr -->
            <div class="flex-1 min-w-0 flex flex-col gap-3">
                <span class="input-label">Choose an opponent</span>
                <div class="flex flex-col gap-2 overflow-y-auto">
                    <PlayCard v-for="u in user"
                        :key="u.id"
                        :user="u"
                        :selected="selectPlayer2 === u.id"
                        @select="toogglePlayer ($event)"
                        ></PlayCard>
                </div>
            </div>
        </div>
        <div class="flex justify-center mt-10">
            <AppButton variant="cta" @click="startMatch">Start game</AppButton>
        </div>
    </div>
</template>