<script setup>
import { computed } from 'vue'
import { calcWinRate } from '@/utils/stats';

const props = defineProps({ node: { type: Object, default: null } })
const rows = computed(() => {
    const n = props.node
    return [
        { label: 'Record', value: n ? `${n.wins}W - ${n.losses}L` : '-'},
        { label: 'Draws', value: n ? n.draws : '-' },
        { label: 'Opponents', value: n ? n.degree : '-' },
    ]
})

const winRate = computed(() => {
    const n = props.node
    if(!n || n.wins + n.losses === 0) return null
    return calcWinRate(n.wins, n.losses)
})
</script>

<template>
    <div class="flex flex-col h-full">
        <div class="input-label">Hover a node</div>
        <div class="text-2xl  mt-2 truncate">{{ node?.nickname ?? '—' }}</div>
        <div class="text-xs text-muted mb-6">{{ node?.isCurrent ? 'you' : ' ' }}</div>

        <div class="flex flex-col gap-3">
            <div v-for="row in rows" :key="row.label"
                class="flex justify-between pb-2 border-b border-dashed border-white/[0.07]">
                <span class="text-[11px] text-muted uppercase tracking-widest">{{ row.label }}</span>
                <span class="text-sm tabular-nums">{{ row.value }}</span>
            </div>
        </div>

        <div class="mt-6">
            <div class="flex justify-between text-[10px] text-muted uppercase tracking-widest mb-1.5">
                <span>Win rate</span><span>{{ winRate === null ? '—' : winRate + '%' }}</span>
            </div>
            <div class="h-1 rounded bg-white/[0.06]">
                <div class="h-full rounded bg-teal transition-[width] duration-300"
                    :style="{ width: (winRate ?? 0) + '%' }"></div>
            </div>
        </div>
    </div>
</template>
