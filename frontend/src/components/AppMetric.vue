<script setup>
// look up object:
defineProps({
    value: String,
    label: String,
    color: { type: String, default: 'white' }
})

const colorMap ={
    white: 'text-white',
    coral: 'text-coral',
    teal: 'text-teal',
    sage: 'text-sage',
    muted: 'text-muted' 
}
</script>

<template>
    <div class="flex flex-col gap-0.5">
        <span class="text-4xl font-light leading-none" :class="colorMap[color]">
            {{ value }}
        </span>
        <span class="text-xs text-muted">{{ label }}</span>
    </div>

</template>