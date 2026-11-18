<script setup>

import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiFetch } from '@/utils/apiFetch'
import { useUserStore } from '@/stores/user'
import { usePresenceStore } from '@/stores/presence'
import AppAvatar from '@/components/AppAvatar.vue'
import AppBadge from '@/components/AppBadge.vue'
import AppButton from '@/components/AppButton.vue'
import AppFilterTabs from '@/components/AppFilterTabs.vue'
import AppPageHeader from '@/components/AppPageHeader.vue'
import LobbyPlayerCard from '@/components/lobby/LobbyPlayerCard.vue'
import OpponentPicker from '@/components/lobby/OpponentPicker.vue'
import { ArrowRight, Keyboard } from 'lucide-vue-next'

    const REMOTE_SOON = 'remote · soon'

    const userStore = useUserStore()
    const presenceStore = usePresenceStore()
    const router = useRouter()
    const route = useRoute()
    const users = ref([])
    const error = ref('')
    const opponentId = ref(null)
    const selectedMode = ref('local')

    async function fetchUsers() {
    try {
        const response = await apiFetch('/api/users/list/')
        if(!response) return
        if(response.ok) {
            const data = await response.json()
            users.value = data
            const invited = Number(route.query.opponent)
            if (invited && data.some(u => u.id === invited)) opponentId.value = invited
        } else {
            router.push('/login')
        }
    } catch (err) {
        error.value = 'Could not load players. Check your connection'
    }
}

// only local mode exists, remote stays as a disabled "soon" option
async function startMatch() {
    error.value = ''
    router.push({ path: '/game', query: { player2: opponentId.value } })
}

onMounted(fetchUsers)

</script>

<template>
    <div class="pb-16 flex flex-col gap-12">
        <AppPageHeader crumb="Transcend · Lobby" title="New match">
            <AppBadge :label="presenceStore.onlineCount + ' online'" variant="teal" />
            <AppFilterTabs v-model="selectedMode"
                :options="['local', REMOTE_SOON]"
                :disabled-options="[REMOTE_SOON]" />
        </AppPageHeader>

        <!-- header stays full width like other pages; the symmetric match panel stays centered -->
        <div v-if="userStore.currentUser" class="w-full max-w-4xl mx-auto flex flex-col gap-8">
            <section class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_72px_minmax(0,1fr)]">
                <LobbyPlayerCard :keys="['W', 'S']">
                    <div class="flex flex-col items-center gap-3 max-w-full min-w-0">
                        <AppAvatar :nickname="userStore.currentUser.nickname" :is-online="true" :avatar="userStore.currentUser.avatar" size="lg" />
                        
                        <div class="max-w-full min-w-0">
                            <div class="text-lg font-light text-muted truncate">{{ userStore.currentUser.nickname }}</div>
                            <div class="text-xs text-muted">You</div>
                        </div>
                    
                    </div>
                </LobbyPlayerCard>

                <!-- horizontal line on a phone, vertical on desktop -->
                <div class="flex lg:flex-col items-center gap-3 h-10 lg:h-auto">
                    <span class="flex-1 h-px lg:h-auto lg:w-px bg-white/[0.07]"></span>
                    <span class="text-xs text-muted tracking-widest">VS</span>
                    <span class="flex-1 h-px lg:h-auto lg:w-px bg-white/[0.07]"></span>
                </div>

                <LobbyPlayerCard :keys="['↑', '↓']">
                    <OpponentPicker v-model="opponentId" :users="users" />
                </LobbyPlayerCard>
            </section>

            <div class="flex flex-col items-center gap-3">
                <AppButton variant="solid" :disabled="opponentId == null" @click="startMatch">
                    Start game
                    <ArrowRight v-if="opponentId != null" :size="16" />
                </AppButton>
                <p v-if="error" class="text-xs text-coral text-center">{{ error }}</p>
                <p v-else class="flex items-center gap-2 text-xs text-muted">
                    <Keyboard :size="14" class="flex-shrink-0" />
                    Same keyboard. Stats save to both players.
                </p>
            </div>
        </div>
    </div>
</template>
