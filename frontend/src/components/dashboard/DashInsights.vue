<script setup>
import { computed } from 'vue'
import { useMatchesStore } from '@/stores/matches';
import { filterByPeriod } from '@/utils/period';
import { opponentStats, pickOpponent } from '@/utils/stats';


const props = defineProps({ period: { type: String, default: 'All' } })
const matchesStore = useMatchesStore()
const periodMatches = computed(() =>
    filterByPeriod(matchesStore.matches, 'ended_at', props.period ))

const rows = computed(() => {
    const opponents = opponentStats(periodMatches.value)
    const best = pickOpponent(opponents, 'wins', 'losses')
    const toughest = pickOpponent(opponents, 'losses', 'wins')
    return [ 
        { label: 'Best opponent',
            value: best?.name ?? '-',
            note: best? `${best.wins}W - ${best.losses}L` :
            'no wins yet' },
        { label: 'Toughest matchup',
            value: toughest?.name ?? '-',
            note: toughest ? `${toughest.wins}W - ${toughest.losses}L` : 'no losses yet'},
        { label: 'Avg rally length', value: '-', note: ''},
    ]
})

</script>






<template>
    <div class="flex flex-col h-full">
        <div class="input-label">At a glance</div>
        <div class="text-sm text-muted mt-1 mb-2">Patterns from your matches</div>

        <div v-for="row in rows"
            :key="row.label"
            class="flex flex-col gap-0.5 py-3 border-b border-dashed border-white/[0.07] last:border-b-0">
            <span class="text-[11px] text-muted uppercase tracking-widest">{{ row.label }}</span>
            <span class="text-xl truncate">{{ row.value }}</span>
            <span v-if="row.note" class="text-xs text-muted">{{ row.note }}</span>
        </div>
    </div>
</template>