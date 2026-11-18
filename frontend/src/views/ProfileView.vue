<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiFetch } from '@/utils/apiFetch'
import { calcWinRate } from '@/utils/stats.js'
import { ArrowRight } from 'lucide-vue-next'
import AppPageHeader from '@/components/AppPageHeader.vue'
import ProfileFriendsBlock from '@/components/profile/ProfileFriendsBlock.vue'
import ProfileInfoCard from '@/components/profile/ProfileInfoCard.vue'

const user = ref(null)
const error = ref('')

const wins = computed(() => user.value?.wins ?? 0)
const losses = computed(() => user.value?.losses ?? 0)
const hasMatches = computed(() => wins.value + losses.value > 0)
const winRate = computed(() => calcWinRate(wins.value, losses.value))

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

onMounted(loadProfile)

</script>

<template>
    <div class="pb-16 flex flex-col gap-10">
        <AppPageHeader crumb="Transcend · Profile" title="Profile" />

        <div v-if="error" class="text-coral text-sm"> {{ error }}</div>
        <div v-if="user" class="grid grid-cols-1 lg:grid-cols-[260px_minmax(0,1fr)] gap-10 lg:gap-12">
            <!-- below sm: stacked; sm..lg: horizontal header (card | stats); lg: left column -->
            <aside class="grid grid-cols-1 sm:grid-cols-[minmax(0,1fr)_260px] lg:grid-cols-1 gap-6 sm:gap-10 lg:gap-6 content-start
                          pb-10 lg:pb-0 lg:pr-12 border-b lg:border-b-0 lg:border-r border-white/[0.07]">
                <ProfileInfoCard :user="user" @updated="loadProfile" />

                <div class="flex flex-col gap-6 sm:justify-center lg:justify-start">
                    <div class="flex flex-col gap-3 pt-6 border-t border-white/[0.07]
                                sm:pt-0 sm:border-t-0 lg:pt-6 lg:border-t">
                        <div class="flex justify-between gap-3">
                            <div>
                                <div class="text-[10px] text-muted uppercase tracking-widest mb-1">Wins</div>
                                <div class="text-2xl font-light text-white tabular-nums leading-none">{{ wins }}</div>
                            </div>
                            <div>
                                <div class="text-[10px] text-muted uppercase tracking-widest mb-1">Losses</div>
                                <div class="text-2xl font-light text-muted tabular-nums leading-none">{{ losses }}</div>
                            </div>
                            <div>
                                <div class="text-[10px] text-muted uppercase tracking-widest mb-1">Win rate</div>
                                <div class="text-2xl font-light text-white tabular-nums leading-none">
                                    {{ hasMatches ? winRate : '—' }}<span v-if="hasMatches" class="text-xs text-muted">%</span>
                                </div>
                            </div>
                        </div>
                        <div class="h-0.5 rounded-full bg-white/[0.07] overflow-hidden">
                            <div class="h-full bg-teal" :style="{ width: winRate + '%' }"></div>
                        </div>
                    </div>

                    <RouterLink to="/dashboard"
                        class="self-end flex items-center gap-1.5 text-xs text-muted hover:text-white transition">
                        Open analytics
                        <ArrowRight :size="14" />
                    </RouterLink>
                </div>
            </aside>

            <ProfileFriendsBlock class="min-w-0" />
        </div>
        <div v-else-if="!error" class="text-muted text-sm">Loading...</div>
    </div>
</template>
