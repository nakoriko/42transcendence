<script setup>
defineProps({
    label: String
})
</script>

<template>
    <span class="bg-navy-800 border border-white/10 rounded-lg text-sage text-xs px-3 py-1">
        {{ label }}
    </span>
</template>