<script setup>
import ArrowsBadge from '../game/ArrowsBadge.vue'

defineProps({ keys: { type: Array, required: true } })
</script>

<template>
    <div class="panel flex flex-col items-center gap-5 py-10 text-center">
        <slot />
        <div class="flex items-center gap-2">
            <ArrowsBadge v-for="key in keys" :key="key" :label="key" />
        </div>
    </div>
</template>