<script setup>
import {computed } from 'vue' 

const props = defineProps({
    wins: Number,
    losses: Number
})

const winRate = computed(()=> {
    const total = (props.wins ?? 0 ) + (props.losses ?? 0)
    if( total == 0) return 0
    return Math.round(props.wins / total * 100)
})

</script>


<template>
<div class="card">
    <div class="input-label mb-4"> Stats</div>

    <div class="flex flex-col gap-2">
        <div class="flex justify-between items-center bg-white/[0.03] rounded-xl px-3 py-2.5">
            <span class="text-xs text-muted">Wins</span>
            <span class="text-2xl font-light text-sage">{{ wins }}</span>
        </div>

        <div class="flex justify-between items-center bg-white/[0.03] rounded-xl px-3 py-2.5">
            <span class="text-xs text-muted">Losses</span>
            <span class="text-2xl font-light text-sage">{{ losses }}</span>
        </div>

        <div class="flex justify-between items-center bg-white/[0.03] rounded-xl px-3 py-2.5">
            <span class="text-xs text-muted">Win Rate</span>
            <span class="text-2xl font-light text-sage">{{ winRate }}%</span>
        </div>

        <div class="mt-1">
            <div class="h-1 bg-white/[0.06] rounded-full overflow-hidden">
                <div class="h-full bg-teal rounded-full transition-all"
                    :style="{ width: winRate + '%'}"></div>
            </div>
            <div class="flex justify-between mt-1">
                <span class="text-[9px] text-muted">0%</span>
                <span class="text-[9px] text-muted">100%</span>
            </div>

        </div>

    </div>

</div>

</template>