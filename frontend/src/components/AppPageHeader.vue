<script setup>

defineProps({
    crumb: { type: String, required: true },
    title: { type: String, required: true},
})
</script>

<template>
    <div class="flex items-center justify-between flex-wrap gap-4">
        <div>
            <p class="input-label mb-1">{{ crumb }}</p>
            <h1 class="page-title">{{ title }}</h1>
        </div>
        <div v-if="$slots.default" class="flex items-center gap-4">
            <slot />
        </div>
    </div>
</template>