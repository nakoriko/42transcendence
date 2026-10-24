<script setup>
import AppFilterTabs from './AppFilterTabs.vue'
import AppBadge from './AppBadge.vue';
import { ref, watch, nextTick } from 'vue'


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
    },
    showIndex: {
    type: Boolean,
    default: true
    }
})

const itemRefs = ref([])

const emit = defineEmits(['filter-change', 'match-click'])

watch(() => props.selectedMatchId, async(id) => {
    if( id === null) return
    await nextTick()
    const index = props.matches.findIndex(m => m.id === id)
    if(index === -1) return

    itemRefs.value[index]?.scrollIntoView({behavior: 'smooth', block: 'center'})
})
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

        <div v-else class="flex-1 min-h-0 flex flex-col gap-1.5 max-h-[400px] overflow-y-auto scroll-thin [scrollbar-gutter:stable]">
            <div v-for="(match, index) in matches" :key="match.id"
                :ref="el => itemRefs[index] = el"
                @click="emit('match-click', match)"
                :class="selectedMatchId === match.id ? 'bg-teal/[0.06]' : 'hover:bg-white/[0.04]'"
                class="grid grid-cols-[2fr_auto_1fr] items-center gap-4
                        rounded-[12px] px-4 py-5 transition cursor-pointer">
                <div class="flex items-center gap-4 min-w-0">
                    <span v-if="showIndex" class="text-sm text-muted font-light bg-sage/[0.04] rounded-md px-2 py-1 flex-shrink-0">#{{ index + 1 }}</span>
                    <div class="min-w-0">
                        <div class="text-base font-light text-white truncate">vs {{ match.opponent_nickname }}</div>
                        <div class="text-xs text-muted">
                            {{ new Date(match.ended_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) }}
                        </div>
                    </div>
                </div>

                <span :class="{ 'invisible': !showScore }" 
                    class="text-sm text-muted text-center bg-sage/[0.04] rounded-md px-4 py-1">
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