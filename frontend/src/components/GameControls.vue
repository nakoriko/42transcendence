<script setup>
import AppBadge from './AppBadge.vue';

</script>

<template>
    <div class="flex gap-12">

        <div class="flex flex-col items-center gap-2">
            <span class="text-xs text-muted uppercase tracking-widest">Player 1</span>
            <div class="flex gap-2">
                <AppBadge label="W"></AppBadge>
                <AppBadge label="S"></AppBadge>
            </div>
        </div>

        <div class="flex flex-col items-center gap-2">
            <span class="text-xs text-muted uppercase tracking-widest">Player 2</span>
            <div class="flex gap-2">
                <AppBadge label="↑"></AppBadge>
                <AppBadge label="↓"></AppBadge>
            </div>
        </div>
    </div>
</template>