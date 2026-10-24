<script setup>
import AppFilterTabs from './AppFilterTabs.vue'
import { ref, watch, nextTick, useSlots } from 'vue'


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
const slots = useSlots()

const emit = defineEmits(['filter-change', 'match-click'])

watch(() => props.selectedMatchId, async(id) => {
    if( id === null) return
    await nextTick()
    const index = props.matches.findIndex(m => m.id === id)
    if(index === -1) return

    itemRefs.value[index]?.scrollIntoView({
        behavior: 'smooth', 
        block: slots.details ? 'nearest' : 'center' })
})
</script>


<template>
    <div class="flex flex-col">
        <div class="flex items-center justify-between h-11 border-b border-white/[0.07]">
            <span class="input-label">Recent Matches</span>
            <AppFilterTabs
                :modelValue="activeFilter"
                :options="['all', 'wins', 'losses']" 
                @update:modelValue="emit('filter-change', $event)"/>
        </div>

        <div v-if="matches.length === 0" class="text-[11px] text-muted py-4">
            No matches yet
        </div>

        <div v-else class="flex-1 min-h-0 flex flex-col max-h-[400px] overflow-y-auto scroll-thin [scrollbar-gutter:stable]">
            <!-- match card: row + expanded block live between the same two lines -->
            <div v-for="(match, index) in matches" :key="match.id"
                :ref="el => itemRefs[index] = el"
                class="border-b border-white/[0.07]">
                <div
                    @click="emit('match-click', match)"
                    :class="{ 'hover:bg-white/[0.03]': selectedMatchId !== match.id }"
                    class="grid grid-cols-[2fr_auto_1fr] items-center gap-4
                            px-3 py-4 transition cursor-pointer">
                    <div class="flex items-center gap-4 min-w-0">
                        <span v-if="showIndex" class="text-sm text-muted font-light tabular-nums flex-shrink-0">
                            {{ String(index + 1).padStart(2, '0') }}
                        </span>
                        <div class="min-w-0">
                            <div class="text-base font-light text-white truncate">vs {{ match.opponent_nickname }}</div>
                            <div class="text-xs text-muted">
                                {{ new Date(match.ended_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) }}
                            </div>
                        </div>
                    </div>

                    <span :class="{ 'invisible': !showScore }" 
                        class="text-sm text-muted text-center tabular-nums">
                        {{ match.score }}
                    </span>
                    <span class="justify-self-end text-xs tracking-widest"
                        :class="match.result === 'win' ? 'text-teal' : 'text-coral'">
                        {{ match.result === 'win' ? 'WIN' : 'LOSS' }}
                    </span>
                </div>

                <!-- expanded block under the selected match, only where the parent passes #details (dashboard) -->
                <div v-if="$slots.details && selectedMatchId === match.id" class="px-3 pb-4">
                    <slot name="details" :match="match" />
                </div>
            </div>
        </div>
    </div>
</template>
