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
    <!-- <hr class="border-white/[0.08] my-4" /> -->

    <!-- <div class="input-label mb-4"> Your Stats</div> -->

    <div class="flex gap-8 items-center mb-8">
        <div class="card flex-1 flex justify-between items-center">
            <div class="flex items-center gap-5">
                <div class="w-15 h-15 bg-white/[0.03] rounded-xl flex items-center justify-center">
                    <Trophy class="w-6 h-6 text-sage" />
                </div>
                <span class="text-xs text-muted">Wins</span>
            </div>
            <span class="text-4xl font-light text-sage px-4">{{ wins }}</span>
        </div>

        <div class="card flex-1 flex justify-between items-center">
            <div class="flex items-center gap-5">
                <div class="w-15 h-15 bg-white/[0.03] rounded-xl flex items-center justify-center">
                    <ThumbsDown class="w-6 h-6 text-sage" />
                </div>
                <span class="text-xs text-muted">Losses</span>
            </div>
            <span class="text-4xl font-light text-sage px-4">{{ losses }}</span>
        </div>

        <div class="card flex-1 flex justify-between items-center">
            <div class="flex items-center gap-5">
                <div class="w-15 h-15 bg-white/[0.03] rounded-xl flex items-center justify-center">
                    <PieChart class="w-6 h-6 text-sage" />
                </div>
                <span class="text-xs text-muted">Win Rate</span>
            </div>
            <span class="text-4xl font-light text-sage px-4">{{ winRate }}%</span>
        </div>


        <!-- <div class="mt-1">
            <div class="h-1 bg-white/[0.06] rounded-full overflow-hidden">
                <div class="h-full bg-teal rounded-full transition-all"
                    :style="{ width: winRate + '%'}"></div>
            </div>
            <div class="flex justify-between mt-1">
                <span class="text-[9px] text-muted">0%</span>
                <span class="text-[9px] text-muted">100%</span>
            </div>

        </div> -->

    </div>

</div>

</template>