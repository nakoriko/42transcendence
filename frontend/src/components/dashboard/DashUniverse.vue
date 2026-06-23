<script setup>
import AppFilterTabs from '@/components/AppFilterTabs.vue';
import AppMetric from '@/components/AppMetric.vue';
import { ref } from 'vue'

const period = ref('All')
const stats = {
    // hardcoded for now:
    players: 45,
    matches: 2455,
    reaction: 87,
}

</script>



<template>
    <div>  <!--DashPlayer Stats-->

        <div class="flex items-center justify-between mb-5">
            <div class="text-2xl uppercase mb-4">Pong universe</div>
            <AppFilterTabs v-model="period" :options="['7d', '30d', 'All']"></AppFilterTabs>
        </div>
        <div class="flex gap-8">
            <div class="flex flex-col gap-6 w-56 flex-shrink-0">
                <div class="text-xs text-muted">All players ranked by first match date. Height = total matches played. Color = activity level. Hover any spike to see full player stats.</div>
                <div class="border-t border-white/[0.07]"></div>  <!-- ← дивайдер -->

                <div class="flex flex-col gap-3 mb-1">
                    <div class="input-label">Platform Stats</div>
                    <AppMetric :value="String(stats.players)" label="Total players" color="coral" ></AppMetric>
                    <AppMetric :value="String(stats.matches)" label="Matches played" color="sage" ></AppMetric>
                    <AppMetric :value="String(stats.reaction + ' ms')" label="Global avg reaction" color="teal" ></AppMetric>
                </div>
                <div class="flex items-center gap-2 mt-1">
                    <span class="text-[9px] text-muted uppercase tracking-widest">new</span>
                    <div class="flex-1 h-px bg-gradient-to-r from-teal via-sage to-coral mb-1"></div>
                    <span class="text-[9px] text-muted uppercase tracking-widest">veteran</span>
                </div>
            </div>
            <div class="flex-1">
                <div class="card h-full flex items-center justify-center text-muted text-sm">chart placeholder</div>
            </div>
        </div>
    </div>

</template>
