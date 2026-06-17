<script setup>
defineProps ({
    matches: {
        type: Array,
        default: () => []
    }
})
</script>


<template>
    <div class="card">
        <div class="input-label mb-4">Recent Matches</div>

        <div v-if="matches.length === 0" class="text-[11px] text-muted py-2">
            No matches yet
        </div>

        <div v-else class="flex flex-col gap-1.5">
            <div v-for="match in matches" :key="match.id"
                class="flex items-center justify-between bg-white/[0.03] rounded-lg px-2.5 py-1.5">
                <div>
                    <div class="terxt-[11px] text-white">vs {{ match.opponent_nickname }}</div>
                    <div class="text-[9px] text-muted">{{ new Date(match.ended_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short'}) }}</div>
                </div>
                <span class="text-xs text-muted mx-auto"> {{ match.score }}</span>
                <span :class="match.result === 'win' ? 'badge-win' : 'badge-loss'">
                    {{ match.result === 'win' ? 'WIN' : 'LOSS' }}
                </span>    
            </div>
        </div>
        <div class="text-[10px] text-teal mt-3 cursor-pointer">See full history</div>
    </div>
</template>