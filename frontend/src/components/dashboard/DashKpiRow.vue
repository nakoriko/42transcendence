<script setup>
    import { computed } from 'vue'
    import { useMatchesStore } from '@/stores/matches';
    import { useUserStore } from '@/stores/user';
    import { calcWinRate, summarizeRecord, calcRank } from '@/utils/stats';

    const props = defineProps({ players: { type: Array, default: () => [] } })
    const matchesStore = useMatchesStore()
    const userStore = useUserStore()
    const record = computed(() => summarizeRecord(matchesStore.matches))
    const winRate = computed(() => calcWinRate(record.value.wins, record.value.losses))
    const rank = computed(() => calcRank(props.players, userStore.currentUser?.id))
</script>


<template>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-px bg-white/[0.07] border-y border-white/[0.07]">
        <!-- Record -->
        <div class="bg-navy-900 flex flex-col gap-2.5 py-6 pr-6 sm:pl-6 sm:first:pl-0">
            <div class="card-label mb-0">Record</div>
            <div class="flex items-baseline gap-3 text-4xl font-light leading-none">
                <span class="text-teal">{{record.total ? record.wins : '-'}}</span>
                <span class="text-2xl text-muted">/</span>
                <span class="text-coral">{{record.total ? record.losses : '-'}}</span>
            </div>
            <div class="text-xs text-muted">{{  record.total || '-' }} matches</div>
        </div>

        <!-- Win rate -->
        <div class="bg-navy-900 flex flex-col gap-2.5 py-6 pr-6 sm:pl-6 sm:first:pl-0">
            <div class="card-label mb-0">Win rate</div>
            <div class="text-4xl font-light leading-none">
               {{ record.total ? winRate : '-'}}<span class="text-base text-muted ml-1">%</span>
            </div>
            <div class="text-xs text-muted">wins of all matches</div>
        </div>

        <!-- Rank -->
        <div class="bg-navy-900 flex flex-col gap-2.5 py-6 pr-6 sm:pl-6 sm:first:pl-0">
            <div class="card-label mb-0">Rank</div>
            <div class="text-4xl font-light leading-none">
                #{{ rank.rank ?? '-'}}<span class="text-base text-muted ml-1">
                    of  {{  rank.of || '-' }}</span>
            </div>
            <div class="text-xs text-muted">by wins, then win rate</div>
        </div>
    </div>
</template>

