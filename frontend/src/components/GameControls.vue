<script setup>
import ArrowsBadge from './game/ArrowsBadge.vue';

</script>

<template>
    <div class="flex gap-12">

        <div class="flex flex-col items-center gap-2">
            <span class="text-xs text-muted uppercase tracking-widest">Player 1</span>
            <div class="flex gap-2">
                <ArrowsBadge label="W"></ArrowsBadge>
                <ArrowsBadge label="S"></ArrowsBadge>
            </div>
        </div>

        <div class="flex flex-col items-center gap-2">
            <span class="text-xs text-muted uppercase tracking-widest">Player 2</span>
            <div class="flex gap-2">
                <ArrowsBadge label="↑"></ArrowsBadge>
                <ArrowsBadge label="↓"></ArrowsBadge>
            </div>
        </div>
    </div>
</template>