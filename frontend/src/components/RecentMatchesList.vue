<script setup>
import AppFilterTabs from './AppFilterTabs.vue'
import AppBadge from './AppBadge.vue';
import { ref, computed } from 'vue'


const props = defineProps ({
    matches: {
        type: Array,
        default: () => []
    },
    activeFilter: {
        type: String,
        default: 'all'
    },
    selectedMatchId: {
        type: [Number, String],
        default: null
    },
    showScore: {
        type: Boolean,
        default: true
    }
})
const emit = defineEmits(['filter-change', 'match-click'])
</script>


<template>
    <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
            <span class="input-label">Recent Matches</span>
            <AppFilterTabs
                :modelValue="activeFilter"
                :options="['all', 'wins', 'losses']" 
                @update:modelValue="emit('filter-change', $event)"/>
        </div>

        <div v-if="matches.length === 0" class="text-[11px] text-muted py-2">
            No matches yet
        </div>

        <div v-else class="flex flex-col gap-1.5 max-h-[400px] overflow-y-auto scroll-thin [scrollbar-gutter:stable]">
            <div v-for="(match, index) in matches" :key="match.id"
            @click="emit('match-click', match)"
            :class="selectedMatchId === match.id ? 'bg-teal/[0.06]' : 'hover:bg-white/[0.04]'"
            class="grid grid-cols-[1fr_auto_1fr] items-center gap-4 
                rounded-[12px] px-4 py-5 transition cursor-pointer">
                <!-- class="grid grid-cols-[1fr_auto_1fr] items-center gap-4
                        rounded-[12px] px-4 py-5 hover:bg-white/[0.04] transition"> -->

                <div class="flex items-center gap-4 min-w-0">
                    <span class="text-xl text-muted font-light bg-sage/[0.04] rounded-md px-2 py-1 flex-shrink-0">#{{ index + 1 }}</span>
                    <div class="min-w-0">
                        <div class="text-base font-light text-white truncate">vs {{ match.opponent_nickname }}</div>
                        <div class="text-xs text-muted">
                            {{ new Date(match.ended_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) }}
                        </div>
                    </div>
                </div>

                    <span :class="{ 'invisible': !showScore }" 
                        class="text-xl text-muted text-center bg-sage/[0.04] rounded-md px-4 py-1">
                        {{ match.score }}
                    </span>                
                    <AppBadge
                    class="justify-self-end"
                    :label="match.result === 'win' ? 'WIN' : 'LOSS'"
                    :variant="match.result === 'win' ? 'sage' : 'coral'" />

            </div>
        </div>
    </div>
</template>