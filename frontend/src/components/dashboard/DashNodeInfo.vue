<script setup>
</script>
<template>
    <div class="flex flex-col h-full">
        <div class="input-label">Hover a node</div>
        <div class="text-2xl font-semibold mt-2">—</div>
        <div class="text-xs text-muted mb-6">&nbsp;</div>

        <div class="flex flex-col gap-3">
            <div v-for="label in ['Record', 'Draws', 'Opponents']" :key="label"
                class="flex justify-between pb-2 border-b border-dashed border-white/[0.07]">
                <span class="text-[11px] text-muted uppercase tracking-widest">{{ label }}</span>
                <span class="text-sm tabular-nums">—</span>
            </div>
        </div>

        <div class="mt-6">
            <div class="flex justify-between text-[10px] text-muted uppercase tracking-widest mb-1.5">
                <span>Win rate</span><span>—</span>
            </div>
            <div class="h-1 rounded bg-white/[0.06]"></div>
        </div>
    </div>
</template>
