<script setup>
import { ref, computed, onMounted, watch } from 'vue' 
import RecentMatchesList from '../RecentMatchesList.vue'
import DashRallyTimeline from './DashRallyTimeline.vue'
import { apiFetch } from '@/utils/apiFetch.js'
import { useMatchesStore } from '@/stores/matches.js'
import { useUserStore } from '@/stores/user.js'

const matchesStore = useMatchesStore()
const userStore = useUserStore()
const activeFilter  = ref('all')
const selectedMatch = ref(null)
const events        = ref([])         
// const currentUserId = computed(() => userStore.currentUser?.id ?? null)      

const props = defineProps({
    activeMatchId: { type: Number, default: null }
})

onMounted(() => {
    matchesStore.load()
})

const filteredMatches = computed(() => {
    const list = matchesStore.matches
    if (activeFilter.value === 'wins')   return list.filter(m => m.result === 'win')
    if (activeFilter.value === 'losses') return list.filter(m => m.result === 'loss')
    return list
})

watch(() => props.activeMatchId, (id) => {

    if(!id) return
    const match = matchesStore.matches.find(m =>m.id === id)
    if(!match) return
    selectedMatch.value = match
    const isVisible = filteredMatches.value.some(m => m.id === match.id)
    if(!isVisible) {
        activeFilter.value = 'all'
    }
})

watch(selectedMatch, async (match) => {
    events.value = []
    if(!match) return
    const res = await apiFetch(`/api/game/matches/${match.id}/events/`)
    if(!res) return
    const data = await res.json()
    if(selectedMatch.value?.id !== match.id) return 
    events.value = data
})



// const stats = computed(() => {
//     if (!events.value.length) return null
//     const uid = currentUserId.value
//     return {
//         myGoals:  events.value.filter(e => e.event_type === 'goal' && e.player === uid).length,
//         oppGoals: events.value.filter(e => e.event_type === 'goal' && e.player !== uid).length,
//         hits:     events.value.filter(e => e.event_type === 'hit').length,
//         misses:   events.value.filter(e => e.event_type === 'miss').length,
//     }
// })
</script>

<template>
<div class="grid grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)] gap-4">
    <div class="panel">
        <RecentMatchesList
            :matches="filteredMatches"
            :activeFilter="activeFilter"
            :selectedMatchId="selectedMatch?.id ?? null"
            :showScore="true"
            @filter-change="activeFilter = $event"
            @match-click="selectedMatch = $event" />
    </div>
    <div class="panel min-h-[380px]">
        <DashRallyTimeline :match="selectedMatch" :events="events" />
    </div>
    <!-- <MatchEchoViz :match="selectedMatch" :events="events" />  -->
</div>
</template>