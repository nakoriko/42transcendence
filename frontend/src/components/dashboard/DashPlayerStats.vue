<script setup>
import AppFilterTabs from '../AppFilterTabs.vue';
import AppMetric from '../AppMetric.vue';
import { ref } from 'vue'

const period = ref('All')
const stats = {
    // hardcoded for now:
    wins: 24,
    losses: 11,
    winRate: 69,
}

</script>

<template>
    <div>  <!--DashPlayer Stats-->
        <div class="flex items-center justify-between mb-5">
            <div class="input-label mb-4">PLayer Stats</div>
            <AppFilterTabs v-model="period" :options="['7d', '30d', 'All']"></AppFilterTabs>
        </div>
        <div class="flex items-center gap-8 mb-1">
            <AppMetric :value="String(stats.wins)" label="Wins" color="teal" ></AppMetric>
            <AppMetric :value="String(stats.losses)" label="Losses" color="coral" ></AppMetric>
            <AppMetric :value="String(stats.winRate + '%')" label="Win Rate" color="sage" ></AppMetric>
        </div>
        <div class="card h-64 flex items-center justify-center text-muted text-sm">chart placeholder</div>
    </div>

</template>
                
                
