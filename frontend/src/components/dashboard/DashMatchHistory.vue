<script setup>
import { ref, computed, onMounted, watch } from 'vue'  // ← добавили watch
import RecentMatchesList from '../RecentMatchesList.vue'
import MatchEchoViz from './MatchEchoViz.vue'
import { apiFetch } from '@/utils/apiFetch.js'

const matches       = ref([])
const activeFilter  = ref('all')
const selectedMatch = ref(null)
const events        = ref([])         
const currentUserId = ref(null)       

const props = defineProps({
    activeMatchId: { type: Number, default: null }
})

onMounted(async () => {
    const [matchRes, profileRes] = await Promise.all([
        apiFetch('/api/game/matches/?limit=200'),
        apiFetch('/api/users/profile/')
    ])
    if (matchRes)   matches.value = await matchRes.json()
    if (profileRes) currentUserId.value = (await profileRes.json()).id
})

watch(() => props.activeMatchId, (id) => {

    if(!id) return
    const match = matches.value.find(m =>m.id === id)
    if(match) selectedMatch.value = match
})

watch(selectedMatch, async (match) => {
    events.value = []

    if (!match) { events.value = []; return }
    const res = await apiFetch(`/api/game/matches/${match.id}/events/`)
    
    if (res) events.value = await res.json()
})

const filteredMatches = computed(() => {
    if (activeFilter.value === 'wins')   return matches.value.filter(m => m.result === 'win')
    if (activeFilter.value === 'losses') return matches.value.filter(m => m.result === 'loss')
    return matches.value
})

const stats = computed(() => {
    if (!events.value.length) return null
    const uid = currentUserId.value
    return {
        myGoals:  events.value.filter(e => e.event_type === 'goal' && e.player === uid).length,
        oppGoals: events.value.filter(e => e.event_type === 'goal' && e.player !== uid).length,
        hits:     events.value.filter(e => e.event_type === 'hit').length,
        misses:   events.value.filter(e => e.event_type === 'miss').length,
    }
})
</script>

<template>
<div class="grid grid-cols-2 gap-6 items-stretch">

    <RecentMatchesList
        :matches="filteredMatches"
        :activeFilter="activeFilter"
        :selectedMatchId="selectedMatch?.id ?? null"
        :showScore="true"
        @filter-change="activeFilter = $event"
        @match-click="selectedMatch = $event" />

    <div class="flex-1 flex items-center justify-center">
        <div class="flex-1 flex items-center justify-center">
            <MatchEchoViz :match="selectedMatch" :events="events" />  <!-- ← передаём events -->
        </div>

    </div>

</div>
</template>