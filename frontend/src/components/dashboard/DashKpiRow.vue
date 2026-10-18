<script setup>
    import { computed } from 'vue'
    import { useMatchesStore } from '@/stores/matches';
    import { filterByPeriod } from '@/utils/period';
    import { calcWinRate, summarizeRecord , currentStreak } from '@/utils/stats';

    const props = defineProps({ period: { type: String, default: 'All' } })
    const matchesStore = useMatchesStore()

    const record = computed(() =>
        summarizeRecord (filterByPeriod(matchesStore.matches, 'ended_at', props.period)))
    const winRate = computed(() => calcWinRate(record.value.wins, record.value.losses ))
    const streak = computed(() => currentStreak(matchesStore.matches))
    const last7 = computed(() => matchesStore.matches.slice(0, 7).reverse())

</script>


<template>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Record -->
        <div class="panel flex flex-col gap-2.5">
            <div class="card-label mb-0">Record</div>
            <div class="flex items-baseline gap-3 text-4xl font-light leading-none">
                <span class="text-teal">{{record.total ? record.wins : '-'}}</span>
                <span class="text-2xl text-muted">/</span>
                <span class="text-coral">{{record.total ? record.losses : '-'}}</span>
            </div>
            <div class="text-xs text-muted">{{  record.total || '-' }} matches</div>
        </div>

        <!-- Win rate -->
        <div class="panel flex flex-col gap-2.5">
            <div class="card-label mb-0">Win rate</div>
            <div class="text-4xl font-light leading-none">
               {{ record.total ? winRate : '-'}}<span class="text-base text-muted ml-1">%</span>
            </div>
            <div class="text-xs text-muted">wins of all matches</div>
        </div>

        <!-- Current streak -->
        <div class="panel flex flex-col gap-2.5">
            <div class="card-label mb-0">Current streak</div>
            <div class="text-4xl font-light leading-none"
            :class="streak.result === 'win' ? 'text-teal' : streak.result === 'loss' ? 'text-coral' : ''">
            {{ streak.count ? (streak.result === 'win' ? 'W' : 'L') + streak.count : '-' }}
        </div>
            <div class="flex gap-1">
                <span v-for="match in last7" :key="match.id" 
                    class="w-5 h-[22px] rounded"
                    :class="match.result === 'win' ? 'bg-teal' : match.result === 'loss' ? 'bg-coral' : 'bg-white/[0.2]'"></span>
                <span v-for="i in 7 - last7.length" :key="'empty-' + i"
                    class="w-5 h-[22px] rounded bg-white/[0.06]"></span>
            </div>
        </div>

        <!-- Rank -->
        <div class="panel flex flex-col gap-2.5">
            <div class="card-label mb-0">Rank</div>
            <div class="text-4xl font-light leading-none">
                #—<span class="text-base text-muted ml-1">of —</span>
            </div>
            <div class="text-xs text-muted">—</div>
        </div>
    </div>
</template>
