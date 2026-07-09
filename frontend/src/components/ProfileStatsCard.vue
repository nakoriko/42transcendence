<script setup>
import {computed } from 'vue' 
import { calcWinRate } from '@/utils/stats'
import { Trophy, ThumbsDown, PieChart } from 'lucide-vue-next'


const props = defineProps({
    wins: Number,
    losses: Number
})

// const winRate = computed(()=> {
//     const total = (props.wins ?? 0 ) + (props.losses ?? 0)
//     if( total == 0) return 0
//     return Math.round(props.wins / total * 100)
// })

const winRate = computed(()=> calcWinRate(props.wins, props.losses))

</script>


<template>
<div>
    <div class="flex flex-wrap gap-4 mb-8">
        <div class="card flex-auto min-w-[160px] grid grid-cols-[auto_1fr_auto] items-center gap-4">
                <div class="w-15 h-15 bg-white/[0.03] rounded-xl flex items-center justify-center">
                    <Trophy class="w-6 h-6 text-sage" />
                </div>
                <span class="text-xs text-muted truncate">Wins</span>
                <span class="text-3xl font-light text-sage tabular-nums">{{ wins }}</span>
        </div>

        <div class="card flex-auto min-w-[160px] grid grid-cols-[auto_1fr_auto] items-center gap-4">
                <div class="w-15 h-15 bg-white/[0.03] rounded-xl flex items-center justify-center">
                    <ThumbsDown class="w-6 h-6 text-sage" />
                </div>
                <span class="text-xs text-muted truncate">Losses</span>
                <span class="text-3xl font-light text-sage tabular-nums">{{ losses }}</span>
        </div>

        <div class="card flex-auto min-w-[160px] grid grid-cols-[auto_1fr_auto] items-center gap-4">
                <div class="w-15 h-15 bg-white/[0.03] rounded-xl flex items-center justify-center">
                    <PieChart class="w-6 h-6 text-sage" />
                </div>
                <span class="text-xs text-muted truncate">Win Rate</span>
                <span class="text-3xl font-light text-sage tabular-nums">{{ winRate }}%</span>
        </div>
    </div>
</div>
</template>