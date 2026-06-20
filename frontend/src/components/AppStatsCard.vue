<script setup>

defineProps({
    wins: Number,
    losses: Number
})
</script>

<template>
    <div class="bg-navy-800 border border-white/[0.07] rounded-[16px] flex overflow-hidden">
        <div class="flex-1 flex flex-col items-center py-3 gap-1 border-r border-white/[0.07]">
            <span class="text-2xl font-light text-white">{{ wins }}</span>
            <span class="input-label">Wins</span>
        </div>
        <div class="flex-1 flex flex-col items-center py-3 gap-1">
            <span class="text-2xl font-light text-white">{{ losses }}</span>
            <span class="input-label">Losses</span>
        </div>
    </div>
</template>